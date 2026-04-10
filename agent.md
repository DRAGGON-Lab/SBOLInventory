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
The current implementation should preserve the core behavior while using the plate placement refactor:

- custom `InventoryImplementation`
- custom `StorageCollection`
- controlled vocabulary constants
- storage factories for freezers/shelves/boxes
- implementation factories
- containment helpers
- plate placement helper (`place_in_plate`) using well strings
- well validation (`validate_well_position`)

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
- `place_in_plate`
- `validate_well_position`

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
- accepted plate placements
- rejected invalid wells
- rejected duplicate occupancy (when document context is available)

### 6. Keep notebooks educational
Notebooks should demonstrate realistic usage patterns, not just toy fragments.
