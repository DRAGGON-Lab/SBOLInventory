# SBOLInventory

SBOLInventory models laboratory inventory in SBOL 2 with a mixed hierarchy:

- **Collection-based external storage**: `Fridge4C`, `FridgeMinus80C`, `FridgeMinus20C`, `Shelf`
- **Implementation-based containers**: `SolidMediaPlate`, `Box`
- **Implementation-based contents**: `PlatedStrain`, `BacterialStock`, `ProcuredMaterial`, `DilutedPlasmid`

## Object graph

```text
Fridge4C (Collection)
└── Shelf (Collection)
      └── SolidMediaPlate (Implementation)
            └── PlatedStrain (Implementation)

FridgeMinus80C (Collection)
└── Shelf (Collection)
      └── Box (Implementation)
            └── BacterialStock (Implementation)
            └── ProcuredMaterial (Implementation)

FridgeMinus20C (Collection)
└── Shelf (Collection)
      └── Box (Implementation)
            └── DilutedPlasmid (Implementation)
            └── ProcuredMaterial (Implementation)
```

## Placement semantics

`SolidMediaPlate` and `Box` can define allowed rows/columns.
Placing an item records:

- `item.contained_in_implementation = <container URI>`
- `item.location_row = "A"`
- `item.location_column = "1"`

Implementations also carry `active` status (`1` active, `0` discarded).

## Main helpers

- `place_in_container(container, item, row, column)`
- `move_item(item, new_container, row, column)`
- `remove_from_container(container, item)`
- `discard_implementation(item)`
