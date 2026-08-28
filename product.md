# Product definition

## Purpose

SBOLInventory is an SBOL 3 facility-catalog and run-ledger profile with a pySBOL3 reference implementation. It lets a laboratory publish what spaces, assets, material lots, and qualified capability offerings exist, then preserve which assets and materials a reviewed execution actually used.

It is not a scheduler, device driver, booking system, workflow language, or full LIMS.

## Core promise

```text
a facility contains zones
zones locate assets and material lots
assets expose capabilities
workflows require capabilities
plans bind requirements to qualified assets
runs record material changes and evidence
```

The profile owns facility, zone, asset, material-lot, capability-offering, and run-provenance semantics. Consuming systems own workflows, planning, scheduling, and dispatch. Their interoperability contract is the RDF vocabulary, its invariants, and stable capability and asset identities, not this implementation's Python API.

## Functional requirements

1. A document can represent multiple facilities without allowing cross-facility containment.
2. Zones can nest and can represent physical, environmental, containment, storage, and policy boundaries.
3. Assets can be located, composed from child assets, establish controlled zones, and expose one or more capability offerings.
4. Independently bindable or schedulable units are assets in their own right.
5. Capability offerings carry typed parameters, a control mode, active state, and an explicit qualification level.
6. Public metadata alone cannot mark an offering plannable or executable.
7. Physical material lots remain standard SBOL `Implementation` objects whose `built` reference resolves to an SBOL `Component` design.
8. Container assets declare exact valid positions; placement validates position and occupancy.
9. Location, composition, lifecycle, and material-design graphs are locally validated before serialization.
10. A compiler can query deterministic candidates by capability kind, facility, active state, and minimum qualification.
11. A run records used assets, input lots, generated output lots, material derivations, evidence attachments, and optionally the reviewed plan and executor.
12. Turtle and RDF/XML round trips restore typed pySBOL3 extension objects.
13. Unrelated standard SBOL `Implementation` objects remain valid and are not forced into the inventory profile.
14. A versioned vocabulary, numbered rule catalog, SHACL projection, and valid/invalid RDF fixtures define conformance independently of Python.
15. Every profile validation failure reports a stable `sbolinv-*` rule ID that another implementation can reproduce.

## EBEF acceptance example

The public EBEF catalog is the first reference shape because it exercises the distinctions that a single-robot demo hides:

- basement microbiology and microscopy zones plus a first-floor plant zone;
- instruments that establish controlled interior zones;
- a liquid handler physically inside an anaerobic chamber;
- a composite three-block thermocycler;
- repeated incubators and growth chambers;
- explicit qualification and control metadata without operational claims;
- both short runs and long-lived environmental experiments;
- microscopy and plate-reader evidence as well as transformed materials.

The checked-in example is accepted when it validates, round-trips, exposes three separately bindable thermal-cycling blocks, and returns no plannable or executable liquid-handler candidate until an integration has actually been qualified.

## Consumer boundary

This project does not own a compiler or facility adoption roadmap. A consumer may use the Python implementation directly, or implement the same [versioned profile](spec/0.2/specification.md) with another SBOL library. Cross-language consumers should run the same conformance fixtures and compare serialized RDF and stable rule IDs rather than copy Python-specific factories or query APIs.

Compiler-specific requirement IR, target configuration, allocation, scheduling, execution qualification, and rollout sequencing belong with that compiler. A Rust consumer should normally build profile support on `sbol-rs` before designing its compiler integration.
