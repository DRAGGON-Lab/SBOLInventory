# Agent guidance

## Intended model

Keep this sentence true in the code, examples, and RDF:

```text
a facility contains zones
zones locate assets and material lots
assets expose capabilities
workflows require capabilities
plans bind requirements to qualified assets
runs record material changes and evidence
```

SBOLInventory defines the persistent facility-catalog and run-ledger profile, with a pySBOL3 reference implementation. Consuming systems own workflows, requirement extraction, allocation, scheduling, reviewed plans, and dispatch.

## Modeling rules

- Use pySBOL3 and SBOL 3 vocabulary. Do not reintroduce pySBOL2 classes or global configuration.
- Use `Facility` for a governed site and `Zone` for spatial, environmental, containment, storage, or policy boundaries.
- Use `Asset` for instruments, storage units, labware containers, workstations, and independently schedulable functional units.
- Use `located_in` for direct location, `parent_zone` for nested boundaries, `part_of` for physical composition, and `establishes_zones` for a chamber or controller's interior. Do not duplicate inverse edges.
- Put manufacturer/model facts on `Asset`. Put operation kind, typed constraints, control mode, and qualification on its owned `Capability` offering.
- Model separately reservable capacity as child assets. Do not collapse three independent blocks or modules into a product-specific count field.
- Keep the capability vocabulary open and operation-oriented. Do not create a subclass or schema field for each device model.
- Treat public specifications as `described` at most and use `UnspecifiedControl` when the invocation path is not verified. Promotion to `plannable`, `simulatable`, `executable`, or `qualified` requires evidence from the corresponding integration stage.
- Use `MaterialLot`, a standard SBOL `Implementation`, for physical samples and reagents. Its `built` reference must resolve to a standard SBOL `Component` design.
- Do not represent instruments or empty labware as biological `Implementation` objects merely to make them physical.
- Record transformations as new output lots with `wasDerivedFrom`; do not overwrite the input lot's identity and history.
- Use standard `Activity`, `Usage`, `Plan`, `Association`, `ExperimentalData`, and `Attachment` objects for execution provenance where possible.
- Keep raw RDF/pySBOL3 access available through normal object and document APIs; typed helpers must not make interoperability impossible.

## Validation rules

- Treat [`spec/0.2/specification.md`](spec/0.2/specification.md), `vocabulary.ttl`, and `rules.toml` as normative. README prose, Python classes, and examples are informative implementations of that contract.
- Validate raw RDF with `shapes.ttl`, then run pySBOL3 core validation and `validate_inventory_graph`; no one layer substitutes for the others.
- Preserve stable `sbolinv-*` rule IDs in errors, fixtures, and independent implementations.
- Reject dangling or cross-facility references, hierarchy cycles, malformed typed properties, unknown qualification/control values, duplicate capability kinds on one asset, invalid positions, and double occupancy.
- A duplicate capability on one asset is a modeling prompt: use child assets when the offerings are independently bindable.
- Generic SBOL documents may contain ordinary `Implementation` objects. Apply inventory-specific requirements only when `materialKind` is present.

## Consumer boundary

- A catalog query returns candidates, not a completed plan.
- Consumer capability names must map explicitly to stable capability IRIs; never infer requirements from manufacturer or model strings.
- A compiler owns parameter compatibility, resource allocation, concurrency, scheduling, target validation, and frozen requirement-to-asset bindings.
- Runtime executes reviewed bindings and does not re-plan from a changed catalog.
- Treat serialized RDF and profile invariants as the interoperability boundary. Python helpers are non-normative conveniences.
- Implement cross-language support with the consumer's native SBOL library. For a Rust consumer, extend `sbol-rs` rather than embedding or shelling out to this package.
- Keep consumer- and facility-specific adoption roadmaps in the consumer repository, where they can be grounded in its actual compiler and runtime contracts.
