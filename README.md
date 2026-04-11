# SBOLInventory

SBOLInventory is a Python package for representing laboratory inventory objects in SBOL 2, with a focus on linking **physical implementations** to **storage hierarchy**.

## Updated object graph

```text
Fridge4C (Collection)
└── Shelf (Collection)
      └── SolidMediaPlate (Implementation from MD)
            └── PlatedStrain (Implementation from MD)

FridgeMinus80C (Collection)
└── Shelf (Collection)
      └── Box (Implementation from MD)
            └── BacterialStock (Implementation from MD)
            └── ProcuredMaterial (Implementation from MD)

FridgeMinus20C (Collection)
└── Shelf (Collection)
      └── Box (Implementation from MD)
            └── DilutedPlasmid (Implementation from MD)
            └── ProcuredMaterial (Implementation from MD)
```

## Modeling rules

- `ModuleDefinition` is a design only.
- Physical stored/plated objects must be `InventoryImplementation` objects whose `built` points to the design `ModuleDefinition`.
- `Box` and `SolidMediaPlate` are implementations that can contain other implementations by row/column coordinates.
- Placement requires valid and unoccupied row/column coordinates.
- Every implementation has an `active` flag (`"true"` or `"false"`).

## API highlights

- Storage collections: `make_fridge_minus80`, `make_fridge_minus20`, `make_fridge_4c`, `make_shelf`
- Container implementations: `make_box`, `make_solid_media_plate`
- Item implementations: `make_bacterial_stock`, `make_diluted_plasmid`, `make_procured_material`, `make_plated_strain`
- Placement and movement: `place_in_container`, `move_to_container`, `remove_from_container`
- Lifecycle: `discard_implementation`, `is_active`

## Example

```python
from sbol_inventory import (
    make_document,
    add_all,
    add_child,
    make_fridge_4c,
    make_shelf,
    make_solid_media_plate,
    make_plated_strain,
    place_in_container,
)

doc = make_document()

fridge = make_fridge_4c("https://example.org/storage/4C")
shelf = make_shelf("https://example.org/storage/4C/shelf1", label="Shelf 1")
plate = make_solid_media_plate(
    uri="https://example.org/implementation/plate_001",
    plate_md_uri="https://example.org/designs/plate_md_001",
    allowed_rows=["A", "B", "C"],
    allowed_columns=[1, 2, 3, 4],
)
plated = make_plated_strain(
    uri="https://example.org/implementation/plated_001",
    strain_md_uri="https://example.org/designs/strain_md_001",
)

add_all(doc, [fridge, shelf, plate, plated])
add_child(fridge, shelf)
add_child(shelf, plate)

place_in_container(plate, plated, "A", 1)
```
