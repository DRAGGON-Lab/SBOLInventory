# Architechture

## Overview
SBOLInventory is a small Python library organized around four layers:

1. **namespaces**
2. **schema**
3. **factories**
4. **validation**

An additional lightweight **document** helper module keeps common document assembly tasks centralized.

## Module structure

### `namespaces.py`
Contains:

- extension namespace URI
- SBOL class URIs
- controlled terms for inventory kinds
- controlled terms for storage kinds

### `schema.py`
Contains extension-aware object definitions:

- `InventoryImplementation`
- `StorageCollection`

`InventoryImplementation` carries both:
- high-level storage pointer: `stored_at`
- plate-internal placement metadata:
  - `contained_in_plate`
  - `plate_location`

### `factories.py`
Contains construction helpers for domain objects:

- storage factories (`make_fridge_*`, `make_shelf`, `make_box`)
- implementation factories (`make_*_stock`, `make_solid_media_plate`)
- containment helpers (`add_child`)
- plate placement helper (`place_in_plate`)

### `validation.py`
Contains semantic validation utilities:

- validate an individual item (`validate_item`)
- validate 96-well coordinates (`validate_well_position`)

### `document.py`
Contains helpers for document-level operations such as:

- document creation
- bulk addition of top-level objects
- writing SBOL to disk

## Design rationale

### Why extend `Implementation`
`Implementation` is the right semantic anchor for a physical realization of a design.

### Why split external storage vs plate occupancy
External containers (fridges/shelves/boxes) are naturally modeled as `Collection` hierarchy.
Plate wells are not reusable global storage nodes; they are coordinates local to one physical plate.
Therefore, plate placement is stored directly on the contained implementation.

## Dependency flow

```text
namespaces -> schema -> factories -> validation
                      \-> document
```

## Example object graph

```text
Fridge4C (Collection)
└── Shelf (Collection)
    └── Box (Collection)
        └── SolidMediaPlate (Implementation)

BacterialStock implementation:
  contained_in_plate = <plate URI>
  plate_location     = "A1"
```

## Future evolution

- optional dedicated kinds for plated material (`PLATED_STRAIN`, `PLATED_CULTURE`)
- richer validation of built-object categories
- query helpers for occupancy maps and plate summaries
