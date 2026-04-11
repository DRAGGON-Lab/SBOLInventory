# Architechture

## Core architecture

```text
StorageCollection layer
  FridgeMinus80C / FridgeMinus20C / Fridge4C / Shelf

InventoryImplementation layer
  Box / SolidMediaPlate / BacterialStock / DilutedPlasmid / ProcuredMaterial / PlatedStrain
```

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

- Container implementations (`Box`, `SolidMediaPlate`) define allowed coordinates via:
  - `allowed_rows`
  - `allowed_columns`
- Placed implementations record:
  - `contained_in_implementation`
  - `container_row`
  - `container_column`
- Occupancy checks prevent duplicate active items in the same coordinate.
- Lifecycle management uses `active` state (`"true"` / `"false"`).
