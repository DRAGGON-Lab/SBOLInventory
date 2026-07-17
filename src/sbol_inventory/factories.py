"""Factory functions for storage nodes and inventory implementations."""

from __future__ import annotations

from typing import Iterable, Optional, Sequence

from .namespaces import (
    DILUTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    BOX,
    FRIDGE_MINUS_80,
    FRIDGE_MINUS_20,
    FRIDGE_4C,
    SHELF,
)
from .schema import InventoryImplementation, StorageCollection
from .validation import (
    validate_container_and_item,
    validate_container_position,
    validate_container_spec,
    validate_storage_child,
)


def make_fridge_minus80(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_MINUS_80
    x.temperature_c = -80
    x.allowed_item_kinds = [BOX]
    x.allowed_storage_kinds = [SHELF]
    return x


def make_fridge_minus20(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_MINUS_20
    x.temperature_c = -20
    x.allowed_item_kinds = [BOX]
    x.allowed_storage_kinds = [SHELF]
    return x


def make_fridge_4c(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_4C
    x.temperature_c = 4
    x.allowed_item_kinds = [SOLID_MEDIA_PLATE]
    x.allowed_storage_kinds = [SHELF]
    return x


def make_shelf(uri: str, label: Optional[str] = None) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = SHELF
    if label:
        x.label = label
    return x


def _init_container_layout(
    x: InventoryImplementation,
    rows: Sequence[str],
    columns: Iterable[int],
) -> None:
    normalized_rows, normalized_cols = validate_container_spec(rows, columns)
    x.allowed_rows = normalized_rows
    x.allowed_columns = normalized_cols


def make_box(
    uri: str,
    box_md_uri: str,
    rows: Sequence[str],
    columns: Iterable[int],
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a physical inventory box implementation with explicit layout."""
    x = InventoryImplementation(uri)
    x.inventory_kind = BOX
    x.built = box_md_uri
    x.is_active = 1
    _init_container_layout(x, rows=rows, columns=columns)
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFrom = [design_uri]
    return x


def make_diluted_plasmid(
    uri: str,
    plasmid_cd_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    x = InventoryImplementation(uri)
    x.inventory_kind = DILUTED_PLASMID
    x.built = plasmid_cd_uri
    x.is_active = 1
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFrom = [design_uri]
    return x


def make_bacterial_stock(
    uri: str,
    strain_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    x = InventoryImplementation(uri)
    x.inventory_kind = BACTERIAL_STOCK
    x.built = strain_md_uri
    x.is_active = 1
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFrom = [design_uri]
    return x


def make_procured_material(
    uri: str,
    material_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    x = InventoryImplementation(uri)
    x.inventory_kind = PROCURED_MATERIAL
    x.built = material_md_uri
    x.is_active = 1
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFrom = [design_uri]
    return x


def make_plated_strain(
    uri: str,
    strain_md_uri: str,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    x = InventoryImplementation(uri)
    x.inventory_kind = PLATED_STRAIN
    x.built = strain_md_uri
    x.is_active = 1
    if design_uri:
        x.wasDerivedFrom = [design_uri]
    return x


def make_solid_media_plate(
    uri: str,
    plate_md_uri: str,
    rows: Sequence[str],
    columns: Iterable[int],
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    x = InventoryImplementation(uri)
    x.inventory_kind = SOLID_MEDIA_PLATE
    x.built = plate_md_uri
    x.is_active = 1
    _init_container_layout(x, rows=rows, columns=columns)
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFrom = [design_uri]
    return x


def make_single_well_petri_dish_plate(
    uri: str,
    plate_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a single-well petri dish plate with a 1x1 A1 layout."""
    return make_solid_media_plate(
        uri=uri,
        plate_md_uri=plate_md_uri,
        rows=["A"],
        columns=[1],
        storage_uri=storage_uri,
        design_uri=design_uri,
    )


def make_solid_96_well_plate(
    uri: str,
    plate_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a square plate that exposes the standard 96-well A1-H12 positions."""
    return make_solid_media_plate(
        uri=uri,
        plate_md_uri=plate_md_uri,
        rows=["A", "B", "C", "D", "E", "F", "G", "H"],
        columns=range(1, 13),
        storage_uri=storage_uri,
        design_uri=design_uri,
    )


def make_square_96_position_plate(
    uri: str,
    plate_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Backward-compatible alias for :func:`make_solid_96_well_plate`."""
    return make_solid_96_well_plate(
        uri=uri,
        plate_md_uri=plate_md_uri,
        storage_uri=storage_uri,
        design_uri=design_uri,
    )


def _require_shared_document(*objects: InventoryImplementation | StorageCollection) -> None:
    """Require graph mutations to operate on one document-backed graph."""
    documents = [obj.doc for obj in objects]
    if any(doc is None for doc in documents):
        raise ValueError("Add all related objects to one document before changing inventory location")
    if any(doc is not documents[0] for doc in documents[1:]):
        raise ValueError("All related objects must belong to the same document")


def _clear_direct_storage_parent(child: InventoryImplementation | StorageCollection) -> None:
    """Remove a child's previous direct Collection membership and inverse link."""
    previous_parent_uri = (
        child.parent_storage if isinstance(child, StorageCollection) else child.stored_at
    )
    if previous_parent_uri is None:
        return

    previous_parent = child.doc.find(str(previous_parent_uri))
    if not isinstance(previous_parent, StorageCollection):
        raise ValueError(
            f"{child.identity} refers to missing storage parent {previous_parent_uri}"
        )
    previous_parent.members = [
        member for member in previous_parent.members if str(member) != str(child.identity)
    ]
    if isinstance(child, StorageCollection):
        child.parent_storage = None
    else:
        child.stored_at = None


def add_child(parent: StorageCollection, child: InventoryImplementation | StorageCollection) -> None:
    """Place a direct child in storage while maintaining one authoritative parent."""
    _require_shared_document(parent, child)
    validate_storage_child(parent, child)
    _clear_direct_storage_parent(child)

    if str(child.identity) not in {str(member) for member in parent.members}:
        parent.members = list(parent.members) + [child.identity]
    if isinstance(child, StorageCollection):
        child.parent_storage = parent.identity
        # A fridge defines the default physical-item policy for each shelf it owns.
        if not list(child.allowed_item_kinds):
            child.allowed_item_kinds = list(parent.allowed_item_kinds)
    else:
        child.stored_at = parent.identity


def place_item(storage: StorageCollection, item: InventoryImplementation) -> None:
    """Place an inventory item directly into a storage collection."""
    add_child(storage, item)


def place_in_container(
    container: InventoryImplementation,
    item: InventoryImplementation,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    """Place an inventory item into a container implementation at row/column."""
    _require_shared_document(container, item)
    if str(container.identity) == str(item.identity):
        raise ValueError("An inventory item cannot contain itself")
    normalized_row, normalized_col = validate_container_position(container, row, column)
    validate_container_and_item(container, item)

    if check_occupied and container.doc is not None:
        for existing in container.doc.implementations:
            if not isinstance(existing, InventoryImplementation):
                continue
            if str(existing.identity) == str(item.identity):
                continue
            if (
                str(existing.contained_in_container) == str(container.identity)
                and str(existing.container_row) == normalized_row
                and existing.container_column is not None
                and int(existing.container_column) == normalized_col
            ):
                raise ValueError(
                    f"Position {normalized_row}{normalized_col} in {container.identity} is occupied by "
                    f"{existing.identity}"
                )

    _clear_direct_storage_parent(item)
    item.contained_in_container = container.identity
    item.container_row = normalized_row
    item.container_column = normalized_col


def place_in_plate(
    plate: InventoryImplementation,
    item: InventoryImplementation,
    well: str,
    *,
    check_occupied: bool = True,
) -> None:
    """Compatibility helper for plate placement using a well string like A1."""
    if not isinstance(well, str):
        raise ValueError("Well must be provided as a string like 'A1'")

    normalized_well = well.strip().upper()
    if len(normalized_well) < 2:
        raise ValueError(f"Invalid well position '{well}'. Expected format like 'A1'.")

    row = normalized_well[0]
    column_str = normalized_well[1:]
    if not row.isalpha() or not column_str.isdigit():
        raise ValueError(f"Invalid well position '{well}'. Expected format like 'A1'.")

    column = int(column_str)
    place_in_container(plate, item, row=row, column=column, check_occupied=check_occupied)


def move_item(
    item: InventoryImplementation,
    new_container: InventoryImplementation,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    """Move an already-placed item to a new container position."""
    place_in_container(
        new_container,
        item,
        row=row,
        column=column,
        check_occupied=check_occupied,
    )


def remove_from_container(item: InventoryImplementation) -> None:
    """Remove an item from whatever container position it currently occupies."""
    item.contained_in_container = None
    item.container_row = None
    item.container_column = None


def discard_implementation(item: InventoryImplementation) -> None:
    """Mark an inventory implementation as inactive/discarded."""
    item.is_active = 0
