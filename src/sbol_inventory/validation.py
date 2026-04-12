"""Validation helpers for SBOLInventory."""

from __future__ import annotations

from .namespaces import (
    DILUTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    BOX,
)
from .schema import InventoryImplementation, StorageCollection


KNOWN_KINDS = {
    DILUTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    BOX,
}
CONTAINER_KINDS = {BOX, SOLID_MEDIA_PLATE}


def validate_item(item: InventoryImplementation) -> None:
    """Validate an inventory object at the item level."""
    kind = str(item.inventory_kind)

    if kind not in KNOWN_KINDS:
        raise ValueError(f"Unknown inventory kind: {kind}")

    if not item.built:
        raise ValueError(f"{item.identity} is missing a built reference")


def validate_placement(item: InventoryImplementation, storage: StorageCollection) -> None:
    """Validate whether an item is allowed to be placed in a storage collection."""
    allowed = set(storage.allowed_item_kinds)
    if allowed and str(item.inventory_kind) not in allowed:
        raise ValueError(
            f"{item.identity} of kind {item.inventory_kind} "
            f"is not allowed in storage {storage.identity}"
        )


def validate_container_slot(
    container: InventoryImplementation,
    row: str,
    column: int,
) -> tuple[str, int]:
    """Validate row/column against container's configured allowed rows/columns."""
    if not isinstance(container, InventoryImplementation):
        raise ValueError("Container must be an InventoryImplementation")
    if str(container.inventory_kind) not in CONTAINER_KINDS:
        raise ValueError(
            f"Container {container.identity} must be of kind Box or SolidMediaPlate"
        )

    normalized_row = row.strip().upper()
    if not normalized_row:
        raise ValueError("Row must be a non-empty string")
    try:
        col_num = int(column)
    except (TypeError, ValueError):
        raise ValueError("Column must be an integer") from None

    allowed_rows = {str(r).upper() for r in container.allowed_rows}
    if allowed_rows and normalized_row not in allowed_rows:
        raise ValueError(
            f"Invalid row '{normalized_row}' for {container.identity}. Allowed rows: {sorted(allowed_rows)}"
        )

    allowed_columns = {int(c) for c in container.allowed_columns}
    if allowed_columns and col_num not in allowed_columns:
        raise ValueError(
            f"Invalid column '{col_num}' for {container.identity}. Allowed columns: {sorted(allowed_columns)}"
        )

    return normalized_row, col_num


def validate_container_and_item(
    container: InventoryImplementation,
    item: InventoryImplementation,
) -> None:
    """Validate types and semantics for implementation-in-implementation placement."""
    if not isinstance(container, InventoryImplementation):
        raise ValueError("Container must be an InventoryImplementation")
    if not isinstance(item, InventoryImplementation):
        raise ValueError("Item must be an InventoryImplementation")
    if str(container.inventory_kind) not in CONTAINER_KINDS:
        raise ValueError(
            f"Container {container.identity} must be of kind Box or SolidMediaPlate"
        )
