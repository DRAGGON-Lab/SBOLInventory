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
)


def make_fridge_minus80(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_MINUS_80
    x.temperature_c = -80
    x.allowed_item_kinds = [BOX]
    return x


def make_fridge_minus20(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_MINUS_20
    x.temperature_c = -20
    x.allowed_item_kinds = [BOX]
    return x


def make_fridge_4c(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_4C
    x.temperature_c = 4
    x.allowed_item_kinds = [SOLID_MEDIA_PLATE]
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
        x.wasDerivedFroms = [design_uri]
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
        x.wasDerivedFroms = [design_uri]
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
        x.wasDerivedFroms = [design_uri]
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
        x.wasDerivedFroms = [design_uri]
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
        x.wasDerivedFroms = [design_uri]
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
        x.wasDerivedFroms = [design_uri]
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


def add_child(parent: StorageCollection, child: InventoryImplementation | StorageCollection) -> None:
    """Attach a storage node or inventory item to a parent collection."""
    parent.members.append(child.identity)
    if isinstance(child, StorageCollection):
        child.parent_storage = parent.identity
    else:
        child.stored_at = parent.identity


def place_item(storage: StorageCollection, item: InventoryImplementation) -> None:
    """Place an inventory item directly into a storage collection."""
    storage.members.append(item.identity)
    item.stored_at = storage.identity


def place_in_container(
    container: InventoryImplementation,
    item: InventoryImplementation,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    """Place an inventory item into a container implementation at row/column."""
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
                and int(existing.container_column) == normalized_col
            ):
                raise ValueError(
                    f"Position {normalized_row}{normalized_col} in {container.identity} is occupied by "
                    f"{existing.identity}"
                )

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
