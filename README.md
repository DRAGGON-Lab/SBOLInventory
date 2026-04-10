# SBOLInventory

SBOLInventory is a Python package for representing laboratory inventory objects in SBOL 2, with a focus on linking **physical implementations** to **storage hierarchy** in a way that is compatible with SynBioHub workflows.

The package wraps the core ideas in the initial prototype into a reusable library:

- `InventoryImplementation` extends SBOL `Implementation`
- `StorageCollection` extends SBOL `Collection`
- factory functions create typed inventory objects and storage nodes
- containment helpers connect freezers, shelves, boxes, and stored items
- plate occupancy is recorded directly on the placed implementation (`contained_in_plate`, `plate_location`)
- validation helpers enforce placement and well rules

## Scope

This repository is intentionally focused on **SBOL manipulation only**. It does not include:

- a web server
- a frontend
- SynBioHub authentication flows
- machine learning

Those can be built later on top of this package.

## Domain model

### Inventory implementations
- `ExtractedPlasmid`
- `BacterialStock`
- `SolidMediaPlate`

### Storage hierarchy (Collection-based)
- `FridgeMinus80C`
- `FridgeMinus20C`
- `Fridge4C`
- `Shelf`
- `Box`

Plate wells are **not** modeled as first-class objects. Instead, placement is represented as:
- `item.contained_in_plate = <plate URI>`
- `item.plate_location = "A1"`

## Repository structure

```text
SBOLInventory/
├── README.md
├── product.md
├── architechture.md
├── agent.md
├── pyproject.toml
├── .gitignore
├── src/
│   └── sbol_inventory/
│       ├── __init__.py
│       ├── namespaces.py
│       ├── schema.py
│       ├── factories.py
│       ├── validation.py
│       └── document.py
├── tests/
│   └── test_validation.py
└── notebooks/
    └── sbol_inventory_examples.ipynb
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Quick example

```python
import sbol2 as sbol
from sbol_inventory import (
    make_fridge_4c,
    make_shelf,
    make_box,
    make_solid_media_plate,
    make_bacterial_stock,
    add_child,
    place_in_plate,
    validate_well_position,
)

doc = sbol.Document()

fridge = make_fridge_4c("https://example.org/storage/4C")
shelf = make_shelf("https://example.org/storage/4C/shelf1", label="Shelf 1")
box = make_box("https://example.org/storage/4C/shelf1/box1", label="Box 1")
plate = make_solid_media_plate(
    uri="https://example.org/implementation/plate_001",
    plate_md_uri="https://example.org/designs/solid_media_plate_type",
    storage_uri=box.identity,
)
plated_sample = make_bacterial_stock(
    uri="https://example.org/implementation/plated_stock_001",
    strain_md_uri="https://example.org/designs/strain_md_001",
)

for obj in [fridge, shelf, box, plate, plated_sample]:
    doc.add(obj)

add_child(fridge, shelf)
add_child(shelf, box)
add_child(box, plate)

validate_well_position("A1")
place_in_plate(plate, plated_sample, "A1")
```

## Design principles

- Keep storage hierarchy explicit and queryable using collections.
- Model plate-internal occupancy as metadata on implementations, not as slot objects.
- Use SBOL-native top-level objects where possible.
- Keep the package small and composable so it can become a backend dependency later.
- Favor deterministic helper functions over framework-heavy abstractions.

## Next steps

Recommended follow-on work after this repository is stable:

1. add serialization helpers and round-trip parsing examples
2. add stronger semantic validation
3. add CI and packaging release workflow
4. integrate into a service that submits to SynBioHub
