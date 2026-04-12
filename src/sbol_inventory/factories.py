"""Factory functions for storage nodes and inventory implementations."""

from __future__ import annotations

from typing import Optional, Sequence

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
from .validation import validate_container_and_item, validate_container_slot


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


def _set_allowed_grid(
    container: InventoryImplementation,
    allowed_rows: Sequence[str] | None,
    allowed_columns: Sequence[int] | None,
) -> None:
    if allowed_rows:
        container.allowed_rows = [str(r).upper() for r in allowed_rows]
    if allowed_columns:
        container.allowed_columns = [int(c) for c in allowed_columns]


def make_box(
    uri: str,
    box_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
    allowed_rows: Sequence[str] | None = None,
    allowed_columns: Sequence[int] | None = None,
) -> InventoryImplementation:
    """Create a box implementation that can contain inventory at row/column coordinates."""
    x = InventoryImplementation(uri)
    x.inventory_kind = BOX
    x.built = box_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    _set_allowed_grid(x, allowed_rows, allowed_columns)
    return x


def make_diluted_plasmid(
    uri: str,
    plasmid_cd_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a diluted plasmid implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = DILUTED_PLASMID
    x.built = plasmid_cd_uri
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
    """Create a bacterial stock implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = BACTERIAL_STOCK
    x.built = strain_md_uri
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
    """Create procured material implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = PROCURED_MATERIAL
    x.built = material_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def make_solid_media_plate(
    uri: str,
    plate_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
    allowed_rows: Sequence[str] | None = None,
    allowed_columns: Sequence[int] | None = None,
) -> InventoryImplementation:
    """Create a solid media plate implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = SOLID_MEDIA_PLATE
    x.built = plate_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    _set_allowed_grid(x, allowed_rows, allowed_columns)
    return x


def make_plated_strain(
    uri: str,
    strain_md_uri: str,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create plated strain implementation from a strain ModuleDefinition."""
    x = InventoryImplementation(uri)
    x.inventory_kind = PLATED_STRAIN
    x.built = strain_md_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def _append_member(parent: StorageCollection, child_identity: str) -> None:
    members = parent.members
    if hasattr(members, "add"):
        members.add(child_identity)
    else:
        members.append(child_identity)


def add_child(parent: StorageCollection, child) -> None:
    """Attach a storage node or inventory item to a parent collection."""
    _append_member(parent, child.identity)
    if isinstance(child, StorageCollection):
        child.parent_storage = parent.identity
    elif isinstance(child, InventoryImplementation):
        child.stored_at = parent.identity


def place_in_container(
    container: InventoryImplementation,
    item: InventoryImplementation,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    """Place an inventory implementation into a box/plate coordinate."""
    validate_container_and_item(container, item)
    normalized_row, normalized_column = validate_container_slot(container, row, column)

    if check_occupied and container.doc is not None:
        for existing in container.doc.implementations:
            if not isinstance(existing, InventoryImplementation):
                continue
            if existing.identity == item.identity:
                continue
            if (
                str(existing.contained_in_implementation) == str(container.identity)
                and str(existing.location_row).upper() == normalized_row
                and int(existing.location_column) == normalized_column
                and bool(existing.active)
            ):
                raise ValueError(
                    f"Position {normalized_row}{normalized_column} in {container.identity} is occupied by "
                    f"{existing.identity}"
                )

    item.contained_in_implementation = container.identity
    item.location_row = normalized_row
    item.location_column = str(normalized_column)


def remove_from_container(
    container: InventoryImplementation,
    item: InventoryImplementation,
) -> None:
    """Remove an item from a container by clearing location metadata."""
    if str(item.contained_in_implementation) != str(container.identity):
        raise ValueError(f"{item.identity} is not placed in {container.identity}")

    item.contained_in_implementation = None
    item.location_row = ""
    item.location_column = ""


def move_item(
    item: InventoryImplementation,
    new_container: InventoryImplementation,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    """Move an item to a new container position."""
    place_in_container(
        new_container,
        item,
        row,
        column,
        check_occupied=check_occupied,
    )


def discard_implementation(item: InventoryImplementation) -> None:
    """Mark an implementation as inactive/discarded."""
    item.active = False
