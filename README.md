# SBOLInventory

SBOLInventory is a Python package for SBOL 2 inventory modeling that separates:

- **external storage hierarchy** (`Collection`): fridges and shelves
- **physical containers/items** (`Implementation`): boxes, plates, and contained materials

It is an SBOL extension layer: fridges, shelves, coordinates, and lifecycle
state are custom RDF annotations on standards-compliant SBOL Collections and
Implementations. A SynBioHub browser will therefore display generic SBOL
objects; inventory-aware clients should interpret the SBOLInventory namespace.

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

## Graph invariants

The direct location graph is deliberately unambiguous:

```text
Fridge --sbol:member--> Shelf --sbol:member--> Box or Plate
Item --containedInContainer + row + column--> Box or Plate
```

- A shelf or direct inventory object has exactly one direct storage parent.
- A contained item is not also a direct member of a shelf and does not have
  `storedAt`; its storage path is derived through its container.
- Placement, reparenting, and occupancy checks require all related objects to
  be in the same `Document`. Add objects first, then create location edges.
- A 4 C fridge propagates a plate-only policy to its shelves; −20 C and −80 C
  fridges propagate a box-only policy.

Use `validate_inventory_graph(doc)` before upload. `write_rdfxml` performs this
local validation by default; its optional `validate=True` additionally invokes
the online SBOL validator.

## SynBioHub-stable URIs

Do not pass a full URI to a factory while pySBOL2 compliant URI mode is enabled.
Factories accept a display ID in this mode. Before creating any objects, set the
exact namespace that SynBioHub will use for the submission collection:

```python
from sbol_inventory import configure_synbiohub

configure_synbiohub(
    "https://synbiohub.org/user/Gon/<submission_collection_id>"
)
```

This selects untyped SBOL identities, such as
`https://synbiohub.org/user/Gon/<submission_collection_id>/fridge_4c/1`, rather
than pySBOL2's unsafe default `http://examples.org/Collection/...` URI. Choose
the submission collection ID before construction and use that same ID in the
SynBioHub submission. After upload, download the root collection's SBOL and
compare identities, `sbol:member` edges, and inventory annotations before
promoting the data.

## Example

```python
from sbol_inventory import (
    configure_synbiohub,
    make_document,
    add_all,
    make_fridge_4c,
    make_shelf,
    make_solid_media_plate,
    make_plated_strain,
    add_child,
    place_in_container,
    validate_inventory_graph,
    write_rdfxml,
)

# SynBioHub identity namespace. Factory identifiers below are display IDs.
configure_synbiohub("https://synbiohub.org/user/Gon/inventory_2026")

# Storage hierarchy (Collections)
doc = make_document()
fridge4 = make_fridge_4c("fridge_4c")
shelf = make_shelf("fridge_4c_shelf_1")

# Physical containers/items (Implementations)
plate = make_solid_media_plate(
    uri="plate_001",
    plate_md_uri="https://synbiohub.org/user/Gon/inventory_2026/plate_design/1",
    rows=["A", "B", "C"],
    columns=range(1, 5),
)
plated_strain = make_plated_strain(
    uri="plated_strain_001",
    strain_md_uri="https://synbiohub.org/user/Gon/inventory_2026/strain_design/1",
)

add_all(doc, [fridge4, shelf, plate, plated_strain])
add_child(fridge4, shelf)
add_child(shelf, plate)

# Place by row/column, validated against allowed and occupancy
place_in_container(plate, plated_strain, row="A", column=1)
validate_inventory_graph(doc)
write_rdfxml(doc, "inventory.xml")
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
- `configure_synbiohub(...)`
- `validate_inventory_graph(...)`
