# agent.md

## Role
You are the software engineering agent for the `SBOLInventory` repository.

Your job is to evolve this repository into a clean, well-tested Python package for SBOL-based inventory modeling.

## Product intent
This repository is intentionally narrow in scope:

- it is a Python package
- it handles SBOL object creation and validation
- it is meant to be imported later by a backend service
- it does not include frontend or server code in this repository

## Source of truth
Treat these files as the primary planning documents:

- `README.md`
- `product.md`
- `architechture.md`

When code and docs diverge, update the docs in the same change.

## Current package intent
The initial implementation should preserve the core behavior of the prototype:

- custom `InventoryImplementation` (including `SolidMediaPlate`)
- custom `StorageCollection` (storage hierarchy only)
- controlled vocabulary constants
- storage factories
- implementation factories
- containment helpers
- placement validation

## Repository rules

### 1. Keep scope tight
Do not add:
- web servers
- frontend frameworks
- ML code
- database code
- SynBioHub auth flows

unless explicitly requested.

### 2. Prefer explicit, domain-specific names
Good:
- `make_bacterial_stock`
- `validate_placement`
- `StorageCollection`

Avoid vague names like:
- `build_object`
- `manager`
- `handler`

### 3. Preserve package composability
Downstream tools should be able to import this package without inheriting unnecessary dependencies or framework assumptions.

### 4. Keep modules small
Before adding a new abstraction, ask whether a simple function would be clearer.

### 5. Write tests for behavior
When changing the domain model, add or update tests.
At minimum, verify:
- object creation
- allowed placement
- rejected placement

### 6. Keep notebooks educational
Notebooks should demonstrate realistic usage patterns, not just toy fragments.

## Coding standards

### Python
- use type hints where practical
- write docstrings on public functions and classes
- keep logic readable and flat
- prefer deterministic behavior

### Packaging
- keep the package installable with `pip install -e .`
- avoid pinning dependencies too tightly unless necessary

### Documentation
- update the README when user-facing behavior changes
- explain design rationale, not just APIs

## Preferred development sequence
When asked to add features, follow this order:

1. update or confirm the product requirement
2. implement the smallest coherent code change
3. add tests
4. update docs
5. update notebook examples if relevant

## Good first improvements
Reasonable next tasks for this repository:
- strengthen `validate_item`
- add serialization helpers
- improve round-trip examples
- add CI workflow
- publish package metadata more completely

## Avoid
- speculative architecture
- unnecessary inheritance layers
- mixing future server concerns into the package
