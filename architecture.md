# Architecture

## The model in six lines

```text
a facility contains zones
zones locate assets and material lots
assets expose capabilities
workflows require capabilities
plans bind requirements to qualified assets
runs record material changes and evidence
```

This is one end-to-end domain model with a deliberate implementation boundary. The profile describes persistent facts about facilities and executions. Workflow systems own program order, material ownership, planning, scheduling, and dispatch. Stable RDF identities connect those concerns without requiring a consumer to adopt this repository's Python object model.

## Persistent facility graph

```text
Facility
├── Zone ──parentZone──▶ Zone
├── Asset ──locatedIn──▶ Zone or container Asset
│   ├── CapabilityOffering
│   │   └── PropertyValue*
│   ├── partOf ─────────▶ parent Asset
│   └── establishesZone ▶ controlled Zone
└── MaterialLot ─locatedIn▶ Zone or container Asset
    └── sbol:built ───────▶ sbol:Component
```

All persistent domain nodes are addressable by IRIs. `Facility`, `Zone`, and `Asset` are custom SBOL 3 `TopLevel` types. A capability and each typed parameter are owned `Identified` objects because their identity and lifecycle are scoped to the installed asset that makes the offering.

### Why zones and assets are different

A zone is a boundary: a room, BSL area, anaerobic interior, growth environment, storage area, or policy domain. An asset is a thing: an instrument, cabinet, container, workstation, freezer, or independently reservable device unit.

This avoids treating a room as a device and avoids treating a chamber interior as a box. It also represents the EBEF arrangement directly:

```text
microbiology lab (Zone)
└── Coy chamber 1 (Asset)
    └── establishes anaerobic interior (Zone)
        └── locates Microlab Prep (Asset)
```

### Location, composition, and capacity

`locatedIn` is the authoritative direct custody/spatial edge. `partOf` is physical composition. They are not interchangeable. A ProFlex block is part of its thermocycler; a plate is located in a reader; a liquid handler is located in an anaerobic zone.

Container capacity is represented by explicit `allowedPosition` values. Occupancy is derived from active and inactive objects' direct locations. Inactivation does not silently erase custody: discarding a lot and removing it from a container are separate operations.

Independently schedulable capacity is modeled as child assets, not an integer on the parent. Three ProFlex blocks therefore become three candidate bindings. A descriptive property such as `temperature_zones = 2` stays on each block's thermal-cycling offering because it constrains how that offering behaves but is not independently reservable.

## Designs and material lots

SBOL `Component` describes what a biological or chemical thing is. SBOL `Implementation` describes a physical realization. `MaterialLot` subclasses pySBOL3's standard `Implementation` in Python and retains the standard `sbol:Implementation` RDF type, adding only inventory-profile properties such as facility, location, barcode, lot identifier, freeze date, and lifecycle state.

That choice is important for interoperability. Generic SBOL software still sees a normal `Implementation`, while an inventory-aware reader gets a typed `MaterialLot`. Standard implementations with no `materialKind` remain outside the facility-profile validation rules.

Containers and instruments are `Asset` objects, not fake biological implementations. A plate can be both a physical container asset and the location of material lots in wells; it does not need a fictional `built` biological design.

## Capability offerings

A capability kind is a stable operation IRI such as `LiquidHandling`, `ThermalCycling`, or `AbsorbanceMeasurement`. It is deliberately independent of manufacturer and model. The installed asset records manufacturer/model facts; its offering records operational facts:

- capability kind;
- qualification level;
- control mode;
- active state;
- typed parameters and units.

The vocabulary is open. An adapter may introduce a domain IRI without modifying the schema. What remains closed and validated is the qualification ladder and the supported control-mode vocabulary, because silently accepting a misspelling there could authorize the wrong execution path. `UnspecifiedControl` represents an honest unknown and is the default; it is not treated as manual or machine-executable control.

Qualification belongs to the offering, not the model number. Two nominally identical devices may have different installed options, calibration, integration maturity, or acceptance status.

## Consumer contract

SBOL is unordered and does not by itself express a workflow language's binders, control flow, durable effects, or material-consumption semantics. Workflows therefore do not become RDF objects in this profile.

The profile's responsibility ends with valid catalog and run records. A consuming system owns its requirement representation, capability mapping, feasibility checks, allocation, reviewed bindings, and dispatch. It must not infer requirements from manufacturer or model strings, and it must not treat a candidate query as a completed plan.

The wire contract is the RDF vocabulary and its invariants. The Python classes, factories, and `find_qualified_assets` helper are one reference implementation of that contract; they are not a required client architecture. A consumer in another language should preserve the same RDF terms and validation behavior with its native SBOL stack and use cross-implementation fixtures to test equivalence.

For a Rust consumer, the natural first step is profile support in `sbol-rs`: preserve the extension objects and properties, expose typed access where useful, and implement the profile validation rules. Only then should the consuming compiler map its own checked requirements and execution records onto those native types. Embedding this Python package, shelling out to it, or copying its planner-facing helper API would create the wrong boundary.

This repository deliberately does not contain a roadmap for any particular compiler or facility. Such a plan depends on that consumer's actual IR, target model, validation stages, and runtime, and belongs in the consumer repository. At the semantic boundary, a reviewed plan will generally need to preserve:

- workflow/action requirement identity;
- selected asset identity and capability kind;
- qualification required and observed;
- relevant parameter/capacity decisions;
- catalog identity or digest;
- relevant consumer and backend versions.

Runtime executes this frozen binding and must not re-select a different asset. A catalog change after review should invalidate or explicitly re-review the plan.

## Run ledger

The run ledger uses standard SBOL/PROV structures:

```text
prov:Plan ◀── prov:hadPlan ── prov:Association ── prov:agent
                                  │
prov:Activity (run) ──────────────┘
├── prov:Usage(role=RunAsset) ─────────▶ Asset
├── prov:Usage(role=RunInputMaterial) ─▶ input MaterialLot
├── generated output MaterialLot
│   ├── prov:wasGeneratedBy ───────────▶ run
│   └── fac:derivedFromMaterial ───────▶ input MaterialLot(s)
└── generated ExperimentalData
    ├── prov:wasGeneratedBy ───────────▶ run
    └── sbol:hasAttachment ────────────▶ Attachment
```

Material transformations create new lot identities. They do not overwrite the input lot and thereby destroy its history. Lifecycle or location mutations that matter operationally should likewise be represented as reviewed run outcomes or explicit custody events before this becomes a production LIMS.

## Validation layers

Validation is local and deterministic:

1. SHACL Core validates raw RDF structure, cardinality, node kinds, datatypes, owned-object shape, and the closed qualification/control vocabularies before an object library can normalize malformed input.
2. The underlying SBOL library validates the core SBOL graph; this implementation uses pySBOL3.
3. The procedural profile validator applies the numbered cross-object and graph rules for facility equality, duplicate semantic kinds, location and composition cycles, container coordinates and occupancy, material lineage, and run-usage targets.
4. A consuming planner validates its capability mappings, feasibility constraints, and bindings.
5. An execution backend validates dispatch parameters and hardware-specific safety conditions.

Passing one layer does not imply the next. In particular, a publicly described EBEF instrument is not automatically plannable or executable.

## Serialization

Turtle is preferred for review and version control. RDF/XML remains available for systems that require it. Custom pySBOL3 builders restore typed extension classes on parse. The library does not depend on a network validator for ordinary reads or writes. The normative vocabulary, rule catalog, SHACL shapes, and valid/invalid fixtures live under [`spec/0.2`](spec/0.2/specification.md) and are packaged with source and wheel distributions.
