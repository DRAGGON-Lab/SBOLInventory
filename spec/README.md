# SBOLInventory specification

This directory contains the language-neutral SBOLInventory profile. It is the interoperability contract implemented by the Python package in this repository and intended for independent implementations such as one built on `sbol-rs`.

The current draft is [SBOLInventory Profile 0.2](0.2/specification.md).

The specification artifacts have distinct roles:

- `specification.md` defines the normative model and semantics.
- `vocabulary.ttl` defines the RDF terms used by the profile.
- `rules.toml` is the authoritative, numbered conformance-rule catalog.
- `shapes.ttl` is the SHACL Core projection of locally expressible rules.
- `conformance.md` defines implementation claims and the fixture protocol.
- `fixtures/` contains implementation-neutral RDF examples and counterexamples.

README files, architecture notes, Python docstrings, and the EBEF example are informative. When they disagree with the versioned specification, the specification and its numbered rule catalog control.
