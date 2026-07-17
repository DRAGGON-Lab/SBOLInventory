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

## Authoritative location edges

`sbol:member` is used only for direct physical storage edges:

```text
Fridge Collection -> Shelf Collection -> Box or Plate Implementation
```

An item inside a box or plate is linked only through
`contained_in_container`, `container_row`, and `container_column`. It is not
also a direct shelf member. `parent_storage` and `stored_at` are maintained as
inverse links for direct `sbol:member` edges and are checked by
`validate_inventory_graph`.

## SynBioHub identity model

Call `configure_synbiohub("https://synbiohub.org/<owner>/<submission-id>")`
before constructing objects. In that mode, factory arguments are SBOL display
IDs and pySBOL2 produces untyped identities under the configured namespace.
The submission ID must be selected before object construction so the identity
does not need to change after upload.
