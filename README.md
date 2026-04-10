# SBOLInventory

SBOLInventory is a Python package for representing laboratory inventory objects in SBOL 2, with a focus on linking **physical implementations** to **storage hierarchy** in a way that is compatible with SynBioHub workflows.

The package wraps the core ideas in the initial prototype into a reusable library:

- `InventoryImplementation` extends SBOL `Implementation`
- `StorageCollection` extends SBOL `Collection`
- factory functions create typed inventory objects and storage nodes
- containment helpers connect freezers, shelves, boxes, and stored items
- **plate occupancy is captured directly on the contained item** using plate-relative well metadata
- validation helpers enforce item and well rules

## Scope

This repository is intentionally focused on **SBOL manipulation only**. It does not include:

- a web server
- a frontend
- SynBioHub authentication flows
- machine learning

## Domain model

### Inventory implementations
- `ExtractedPlasmid`
- `BacterialStock`
- `SolidMediaPlate`

### Storage hierarchy
- `FridgeMinus80C`
- `FridgeMinus20C`
- `Fridge4C`
- `Shelf`
- `Box`

## Storage vs plate placement

External storage and plate-internal occupancy are modeled differently:

- **External storage** (fridge/shelf/box) uses `StorageCollection` hierarchy via `members` and `stored_at`.
- **Plate-internal occupancy** does **not** use `Slot` objects.
- A plated sample records:
  - `contained_in_plate = <plate implementation URI>`
  - `plate_location = "A1"`

Well coordinates are therefore scoped to a specific plate.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick example

```python
from sbol_inventory import (
    make_document,
    make_solid_media_plate,
    make_bacterial_stock,
    place_in_plate,
    validate_well_position,
)

# 1) Physical plate implementation (built from a plate ModuleDefinition)
plate = make_solid_media_plate(
    uri="https://example.org/implementation/plate_001",
    plate_md_uri="https://example.org/designs/solid_plate_design",
)

# 2) Physical sample implementation (built from a strain ModuleDefinition)
sample = make_bacterial_stock(
    uri="https://example.org/implementation/plated_strain_001",
    strain_md_uri="https://example.org/designs/strain_md_001",
)

# 3) Place the physical sample into a plate well
place_in_plate(plate, sample, "A1")

assert str(sample.contained_in_plate) == str(plate.identity)
assert str(sample.plate_location) == "A1"

# 4) Validate wells
validate_well_position("H12")  # valid
# validate_well_position("Z99")  # raises ValueError
```

## Design principles

- Keep storage hierarchy explicit and queryable.
- Keep plate wells as simple validated coordinates, not first-class storage objects.
- Use SBOL-native top-level objects where possible.
- Keep the package small and composable so it can become a backend dependency later.

## Next steps

1. add richer built-type checks (e.g., enforce expected design categories)
2. add optional inventory kind(s) for plated material (`PLATED_STRAIN`/`PLATED_CULTURE`)
3. add CI and packaging release workflow
4. integrate into a service that submits to SynBioHub
