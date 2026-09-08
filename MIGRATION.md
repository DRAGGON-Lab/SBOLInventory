# Migrating from 0.1 to 0.2

Version 0.2 is a breaking move from pySBOL2/SBOL 2 to pySBOL3/SBOL 3 and from a storage-only schema to a facility catalog.

## Concept mapping

| 0.1 | 0.2 | Reason |
| --- | --- | --- |
| `StorageCollection` fridge or shelf | `Asset` | A fridge or shelf is a physical facility resource, not a grouping of designs |
| `InventoryImplementation` box or plate | `Asset` with `allowed_positions` | Empty labware and containers are physical assets, not realizations of biological designs |
| `InventoryImplementation` material | `MaterialLot`, a standard `sbol3.Implementation` | Physical material still realizes an SBOL design |
| `ModuleDefinition` design | `sbol3.Component` | SBOL 3 unifies the relevant design representation |
| `sbol:member`, `stored_at`, `parent_storage` | `located_in`, `part_of`, `parent_zone` | One authoritative edge for each semantic relationship |
| row plus column properties | normalized `position`, such as `A1` | Containers declare the exact positions they accept |
| integer `is_active` | boolean `is_active` | Native typed RDF value |
| optional online validation during write | local pySBOL3 plus profile validation | Deterministic writes do not require a network service |

## Factory changes

Zones take explicit facility context; assets and materials take their physical location:

```python
facility = make_facility(ns + "facility")
room = make_zone(ns + "freezer_room", facility=facility, kind=STORAGE_ZONE)
freezer = make_fridge_minus80(
    ns + "freezer_1",
    located_in=room,
)
```

Material factories take an actual SBOL 3 `Component` or its IRI through `built`:

```python
design = sbol3.Component(ns + "strain_design", sbol3.SBO_FUNCTIONAL_ENTITY)
stock = make_bacterial_stock(
    ns + "stock_1",
    built=design,
)
```

Add related top-level objects to one document before using mutation helpers such as `locate`, `place_in_container`, or `move_item`.

Only Zones carry `fac:facility`. Assets and materials use `locatedIn` to reference a Zone or another Asset; component assets without a direct location may inherit membership through `partOf`. Use `facility_identity(obj)` to query derived membership. Unlocated objects have no known facility, so put catalog residents in their actual zone or container before querying a facility.

## Run and repository records

Run helpers accept input and output Components alongside physical materials. Only new designs belong in generated Components; producing a lot from a design does not regenerate the design. `link_evidence` records `fac:forComponent` and shares the ExperimentalData Attachment references with its Component. `record_submission` and `record_retrieval` record completed repository transfers; callers remain responsible for network operations.

## Compatibility names

The following names remain as narrow aliases where their semantics are still honest:

- `discard_implementation` → `discard`
- `make_square_96_position_plate` → `make_solid_96_well_plate`
- `place_item` → `locate`
- `add_child` → direct location without a container position

`InventoryImplementation` and `StorageCollection` are intentionally not aliased. Their RDF types and assumptions are incompatible with the 0.2 model, and a silent alias would misclassify instruments, containers, or designs.

The 0.1 piecemeal validators (`validate_item`, `validate_placement`, `validate_well_position`, `validate_container_spec`, `validate_container_position`, and `validate_container_and_item`) are replaced by validated mutation helpers plus `validate_document`. Use `grid_positions` when only layout normalization is needed.

## Data migration

There is no lossless automatic converter in 0.2. An SBOL 2 document does not contain enough information to decide whether every collection represents a facility zone, an installed storage asset, or a logical grouping, and old container implementations may point to placeholder design objects created only to satisfy SBOL 2 structure.

Migrate deliberately:

1. Convert genuine SBOL 2 biological designs to SBOL 3 `Component` objects with an SBOL-aware converter.
2. Establish a `Facility` and stable `Zone` identities.
3. Reclassify fridges, shelves, boxes, plates, and instruments as `Asset` objects.
4. Recreate physical samples and reagents as `MaterialLot` implementations pointing to the converted components.
5. Translate each authoritative location once; do not copy old inverse or duplicate membership edges.
6. Assign public facts only `described` qualification until planning and execution evidence exists.
7. Run `validate_document`, serialize to Turtle, read it back, and validate the parsed document before promoting the catalog.
