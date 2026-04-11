"""Factory functions for storage nodes and inventory implementations."""

from __future__ import annotations

from typing import Iterable, Optional

from .namespaces import (
    BACTERIAL_STOCK,
    BOX,
    DILUTED_PLASMID,
    FRIDGE_4C,
    FRIDGE_MINUS_20,
    FRIDGE_MINUS_80,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    SHELF,
    SOLID_MEDIA_PLATE,
)
from .schema import InventoryImplementation, StorageCollection
from .validation import (
    is_active,
    validate_container,
    validate_container_position,
)


def _set_active_default(x: InventoryImplementation) -> None:
    if not x.active:
        x.active = "true"


def _set_allowed_grid(
    container: InventoryImplementation,
    allowed_rows: Iterable[str],
    allowed_columns: Iterable[int],
) -> None:
    container.allowed_rows = [str(row).upper() for row in allowed_rows]
    container.allowed_columns = [int(column) for column in allowed_columns]


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


def make_diluted_plasmid(
    uri: str,
    plasmid_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a diluted plasmid implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = DILUTED_PLASMID
    x.built = plasmid_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    _set_active_default(x)
    return x


def make_bacterial_stock(
    uri: str,
    strain_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a bacterial stock implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = BACTERIAL_STOCK
    x.built = strain_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    _set_active_default(x)
    return x


def make_procured_material(
    uri: str,
    material_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a procured material implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = PROCURED_MATERIAL
    x.built = material_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    _set_active_default(x)
    return x


def make_plated_strain(
    uri: str,
    strain_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a plated strain implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = PLATED_STRAIN
    x.built = strain_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    _set_active_default(x)
    return x


def make_box(
    uri: str,
    box_md_uri: str,
    storage_uri: Optional[str] = None,
    allowed_rows: Iterable[str] = tuple("ABCDEFGH"),
    allowed_columns: Iterable[int] = tuple(range(1, 13)),
) -> InventoryImplementation:
    """Create a box implementation with allowed row/column grid."""
    x = InventoryImplementation(uri)
    x.inventory_kind = BOX
    x.built = box_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    _set_allowed_grid(x, allowed_rows, allowed_columns)
    _set_active_default(x)
    return x


def make_solid_media_plate(
    uri: str,
    plate_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
    allowed_rows: Iterable[str] = tuple("ABCDEFGH"),
    allowed_columns: Iterable[int] = tuple(range(1, 13)),
) -> InventoryImplementation:
    """Create a solid media plate implementation with allowed row/column grid."""
    x = InventoryImplementation(uri)
    x.inventory_kind = SOLID_MEDIA_PLATE
    x.built = plate_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    _set_allowed_grid(x, allowed_rows, allowed_columns)
    _set_active_default(x)
    return x


def add_child(parent: StorageCollection, child) -> None:
    """Attach a storage node or inventory item to a parent collection."""
    parent.members.add(child.identity)
    if isinstance(child, StorageCollection):
        child.parent_storage = parent.identity
    elif isinstance(child, InventoryImplementation):
        child.stored_at = parent.identity


def _check_occupancy(
    container: InventoryImplementation,
    row: str,
    column: int,
    moving_item: InventoryImplementation,
) -> None:
    if container.doc is None:
        return

    for existing in container.doc.implementations:
        if not isinstance(existing, InventoryImplementation):
            continue
        if existing.identity == moving_item.identity:
            continue
        if not is_active(existing):
            continue
        if (
            str(existing.contained_in_implementation) == str(container.identity)
            and str(existing.container_row).upper() == row
            and int(existing.container_column) == column
        ):
            raise ValueError(
                f"Position {row}{column} in {container.identity} is already occupied by "
                f"{existing.identity}"
            )


def place_in_container(
    container: InventoryImplementation,
    item: InventoryImplementation,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    """Place an item into a Box or SolidMediaPlate at a row/column."""
    validate_container(container)
    if not isinstance(item, InventoryImplementation):
        raise ValueError("Item must be an InventoryImplementation")

    normalized_row, normalized_column = validate_container_position(container, row, column)

    if check_occupied:
        _check_occupancy(container, normalized_row, normalized_column, item)

    item.contained_in_implementation = container.identity
    item.container_row = normalized_row
    item.container_column = normalized_column


def move_to_container(
    item: InventoryImplementation,
    new_container: InventoryImplementation,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    """Move an item to a new container position."""
    if not isinstance(item, InventoryImplementation):
        raise ValueError("Item must be an InventoryImplementation")

    place_in_container(
        new_container,
        item,
        row,
        column,
        check_occupied=check_occupied,
    )


def remove_from_container(
    container: InventoryImplementation,
    item: InventoryImplementation,
) -> None:
    """Remove an item from a container and clear its position metadata."""
    if str(item.contained_in_implementation) != str(container.identity):
        raise ValueError(
            f"Item {item.identity} is not currently in container {container.identity}"
        )

    item.contained_in_implementation = ""
    item.container_row = ""
    item.container_column = None


def discard_implementation(item: InventoryImplementation) -> None:
    """Mark an implementation as inactive/discarded."""
    if not isinstance(item, InventoryImplementation):
        raise ValueError("Item must be an InventoryImplementation")
    item.active = "false"
