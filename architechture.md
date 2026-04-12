# Architechture

## Summary

SBOLInventory uses a two-layer physical model:

1. **Storage layer** (`StorageCollection`): fridges + shelves
2. **Container/item layer** (`InventoryImplementation`): boxes, plates, and contained implementations

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

## Placement model

Container implementations define allowed coordinates (`allowed_rows`, `allowed_columns`).
Placed items record:
- `contained_in_container`
- `container_row`
- `container_column`

Helpers:
- `place_in_container(...)`
- `move_item(...)`
- `remove_from_container(...)`
- `discard_implementation(...)`
