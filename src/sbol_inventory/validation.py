"""Validation helpers for SBOLInventory."""

from __future__ import annotations

import re
from typing import Iterable, Sequence

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
CONTAINER_KINDS = {SOLID_MEDIA_PLATE, BOX}
WELL_96_RE = re.compile(r"^[A-H](?:[1-9]|1[0-2])$")


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


def validate_well_position(well: str) -> str:
    """Validate and normalize a 96-well location (A1-H12)."""
    if not isinstance(well, str):
        raise ValueError("Well must be provided as a string like 'A1'")

    normalized = well.strip().upper()
    if not WELL_96_RE.match(normalized):
        raise ValueError(
            f"Invalid 96-well position '{well}'. Expected rows A-H and columns 1-12."
        )
    return normalized


def validate_container_spec(rows: Sequence[str], columns: Iterable[int]) -> tuple[list[str], list[int]]:
    """Validate row/column layout declaration for a container."""
    if not rows:
        raise ValueError("Container must define at least one allowed row")

    normalized_rows = [str(r).strip().upper() for r in rows]
    if any(not r.isalpha() or len(r) != 1 for r in normalized_rows):
        raise ValueError("Rows must be single alphabetic labels like ['A', 'B']")

    normalized_cols = [int(c) for c in columns]
    if not normalized_cols:
        raise ValueError("Container must define at least one allowed column")
    if any(c < 1 for c in normalized_cols):
        raise ValueError("Columns must be positive integers")

    return normalized_rows, normalized_cols


def validate_container_position(
    container: InventoryImplementation, row: str, column: int
) -> tuple[str, int]:
    """Validate a row/column placement against a container's allowed positions."""
    normalized_row = str(row).strip().upper()
    normalized_col = int(column)

    if normalized_row not in list(container.allowed_rows):
        raise ValueError(
            f"Row {normalized_row} is not allowed in container {container.identity}; "
            f"allowed rows: {list(container.allowed_rows)}"
        )
    if normalized_col not in list(container.allowed_columns):
        raise ValueError(
            f"Column {normalized_col} is not allowed in container {container.identity}; "
            f"allowed columns: {list(container.allowed_columns)}"
        )

    return normalized_row, normalized_col


def validate_container_and_item(
    container: InventoryImplementation,
    item: InventoryImplementation,
) -> None:
    """Validate implementation-to-container semantics."""
    if not isinstance(container, InventoryImplementation):
        raise ValueError("Container must be an InventoryImplementation")
    if not isinstance(item, InventoryImplementation):
        raise ValueError("Item must be an InventoryImplementation")

    kind = str(container.inventory_kind)
    if kind not in CONTAINER_KINDS:
        raise ValueError(
            f"Container {container.identity} must be one of {sorted(CONTAINER_KINDS)}"
        )
