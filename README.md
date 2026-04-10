# SBOLInventory

SBOLInventory is a Python package for representing laboratory inventory objects in SBOL 2, with a focus on linking **physical implementations** to **storage hierarchy** in a way that is compatible with SynBioHub workflows.

The package wraps the core ideas in the initial prototype into a reusable library:

- `InventoryImplementation` extends SBOL `Implementation`
- `StorageCollection` extends SBOL `Collection`
- factory functions create typed inventory objects and storage nodes
- containment helpers connect freezers, shelves, boxes, slots, and stored items
- validation helpers enforce placement rules

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

All three are represented as `InventoryImplementation` (SBOL `Implementation`)
objects. `SolidMediaPlate` is never modeled as a `Collection`.

### Storage hierarchy
- `FridgeMinus80C`
- `FridgeMinus20C`
- `Fridge4C`
- `Shelf`
- `Box`
- `Slot`

All storage hierarchy nodes are represented as `StorageCollection` (SBOL
`Collection`) objects.

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
    make_fridge_minus80,
    make_shelf,
    make_box,
    make_slot,
    make_bacterial_stock,
    add_child,
    place_item,
    validate_placement,
)

doc = sbol.Document()

freezer = make_fridge_minus80("https://example.org/storage/-80")
shelf = make_shelf("https://example.org/storage/-80/shelf2", label="Shelf 2")
box = make_box("https://example.org/storage/-80/shelf2/box4", label="Box 4")
slot = make_slot(
    "https://example.org/storage/-80/shelf2/box4/A4",
    label="A4",
)

stock = make_bacterial_stock(
    uri="https://example.org/implementation/bstock_001",
    strain_md_uri="https://example.org/designs/strain_md_001",
    slot_uri=slot.identity,
)

for obj in [freezer, shelf, box, slot, stock]:
    doc.add(obj)

add_child(freezer, shelf)
add_child(shelf, box)
add_child(box, slot)
place_item(slot, stock)

validate_placement(stock, slot)
```

### Solid media plate example (as Implementation)

```python
from sbol_inventory import (
    SOLID_MEDIA_PLATE,
    make_fridge_4c,
    make_shelf,
    make_box,
    make_slot,
    make_solid_media_plate,
    add_child,
    place_item,
    validate_placement,
)

fridge4 = make_fridge_4c("https://example.org/storage/4c")
shelf4 = make_shelf("https://example.org/storage/4c/shelf1", label="Shelf 1")
box4 = make_box("https://example.org/storage/4c/shelf1/box1", label="Box 1")
slot4 = make_slot(
    "https://example.org/storage/4c/shelf1/box1/P1",
    label="P1",
    allowed_item_kinds=[SOLID_MEDIA_PLATE],
)

plate = make_solid_media_plate(
    uri="https://example.org/implementation/plate_001",
    plate_md_uri="https://example.org/designs/plate_md_001",
)

add_child(fridge4, shelf4)
add_child(shelf4, box4)
add_child(box4, slot4)
validate_placement(plate, slot4)
place_item(slot4, plate)
```

## Design principles

- Keep the storage hierarchy explicit and queryable.
- Use SBOL-native top-level objects where possible.
- Keep the package small and composable so it can become a backend dependency later.
- Favor deterministic helper functions over framework-heavy abstractions.

## Next steps

Recommended follow-on work after this repository is stable:

1. add serialization helpers and round-trip parsing examples
2. add stronger semantic validation
3. add CI and packaging release workflow
4. integrate into a service that submits to SynBioHub
