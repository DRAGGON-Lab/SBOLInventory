# SBOLInventory

SBOLInventory is a Python package for SBOL 2 inventory modeling that separates:

- **external storage hierarchy** (`Collection`): fridges and shelves
- **physical containers/items** (`Implementation`): boxes, plates, and contained materials

## Object graph

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

## Key concepts

- `ModuleDefinition` is a design.
- Physical items are always `InventoryImplementation` with `built` pointing to the design.
- `SolidMediaPlate` and `Box` are container implementations with explicit allowed row/column layout.
- Placed items record:
  - `contained_in_container`
  - `container_row`
  - `container_column`
- Every implementation has `is_active` and can be discarded (set inactive).

## Example

```python
from sbol_inventory import (
    make_document,
    add_all,
    make_fridge_4c,
    make_shelf,
    make_solid_media_plate,
    make_plated_strain,
    add_child,
    place_in_container,
)

# Storage hierarchy (Collections)
doc = make_document()
fridge4 = make_fridge_4c("https://example.org/storage/4C")
shelf = make_shelf("https://example.org/storage/4C/shelf1")

# Physical containers/items (Implementations)
plate = make_solid_media_plate(
    uri="https://example.org/implementation/plate1",
    plate_md_uri="https://example.org/designs/plate_md",
    rows=["A", "B", "C"],
    columns=range(1, 5),
)
plated_strain = make_plated_strain(
    uri="https://example.org/implementation/plated1",
    strain_md_uri="https://example.org/designs/strain_md",
)

add_all(doc, [fridge4, shelf, plate, plated_strain])
add_child(fridge4, shelf)
add_child(shelf, plate)

# Place by row/column, validated against allowed and occupancy
place_in_container(plate, plated_strain, row="A", column=1)
```

## Main API additions

- `make_box(...)`
- `make_diluted_plasmid(...)`
- `make_procured_material(...)`
- `make_plated_strain(...)`
- `place_in_container(...)`
- `move_item(...)`
- `remove_from_container(...)`
- `discard_implementation(...)`
