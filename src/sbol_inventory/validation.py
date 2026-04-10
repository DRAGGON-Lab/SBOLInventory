"""Validation helpers for SBOLInventory."""

from __future__ import annotations

import re

from .namespaces import EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE
from .schema import InventoryImplementation, StorageCollection


KNOWN_KINDS = {EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE}
WELL_96_PATTERN = re.compile(r"^[A-H](?:[1-9]|1[0-2])$")


def validate_item(item: InventoryImplementation) -> None:
    """Validate an inventory object at the item level."""
    kind = str(item.inventory_kind)

    if kind not in KNOWN_KINDS:
        raise ValueError(f"Unknown inventory kind: {kind}")

    if not item.built:
        raise ValueError(f"{item.identity} is missing a built reference")


def validate_placement(item: InventoryImplementation, slot: StorageCollection) -> None:
    """Validate whether an item is allowed to be placed in a slot."""
    allowed = set(slot.allowed_item_kinds)
    if allowed and str(item.inventory_kind) not in allowed:
        raise ValueError(
            f"{item.identity} of kind {item.inventory_kind} "
            f"is not allowed in slot {slot.identity}"
        )


def validate_well_position(well: str) -> str:
    """Validate and normalize a 96-well plate position."""
    normalized = well.strip().upper()
    if not WELL_96_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"Invalid 96-well plate location: {well!r}. "
            "Expected rows A-H and columns 1-12 (e.g., A1, H12)."
        )
    return normalized
