"""Validation helpers for SBOLInventory."""

from __future__ import annotations

from .namespaces import (
    BACTERIAL_STOCK,
    BOX,
    DILUTED_PLASMID,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    SOLID_MEDIA_PLATE,
)
from .schema import InventoryImplementation, StorageCollection


KNOWN_KINDS = {
    DILUTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    BOX,
    PROCURED_MATERIAL,
    PLATED_STRAIN,
}

VALID_ROWS = tuple("ABCDEFGH")
VALID_COLUMNS = tuple(range(1, 13))
CONTAINER_KINDS = {SOLID_MEDIA_PLATE, BOX}


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


def validate_row_column(row: str, column: int) -> tuple[str, int]:
    """Validate and normalize a row/column pair for a 96-position container."""
    if not isinstance(row, str):
        raise ValueError("Row must be a string from A to H")

    normalized_row = row.strip().upper()
    if normalized_row not in VALID_ROWS:
        raise ValueError(f"Invalid row '{row}'. Expected one of A-H")

    if not isinstance(column, int):
        raise ValueError("Column must be an integer from 1 to 12")

    if column not in VALID_COLUMNS:
        raise ValueError(f"Invalid column '{column}'. Expected one of 1-12")

    return normalized_row, column


def validate_container(container: InventoryImplementation) -> None:
    """Validate a target implementation is a supported placement container."""
    if not isinstance(container, InventoryImplementation):
        raise ValueError("Container must be an InventoryImplementation")

    if str(container.inventory_kind) not in CONTAINER_KINDS:
        raise ValueError(
            "Container must be a SolidMediaPlate or Box implementation"
        )


def validate_container_position(
    container: InventoryImplementation,
    row: str,
    column: int,
) -> tuple[str, int]:
    """Validate a row/column value against container constraints."""
    normalized_row, normalized_column = validate_row_column(row, column)

    allowed_rows = {str(x).upper() for x in container.allowed_rows}
    allowed_columns = {int(x) for x in container.allowed_columns}

    if not allowed_rows or not allowed_columns:
        raise ValueError(
            f"Container {container.identity} is missing allowed_rows or allowed_columns"
        )

    if normalized_row not in allowed_rows:
        raise ValueError(
            f"Row {normalized_row} is not allowed for container {container.identity}"
        )

    if normalized_column not in allowed_columns:
        raise ValueError(
            f"Column {normalized_column} is not allowed for container {container.identity}"
        )

    return normalized_row, normalized_column


def is_active(item: InventoryImplementation) -> bool:
    """Return whether an implementation is active (default True when unset)."""
    value = str(item.active).lower().strip() if item.active else "true"
    return value == "true"
