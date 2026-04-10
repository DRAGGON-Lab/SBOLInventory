"""Validation helpers for SBOLInventory."""

from __future__ import annotations

import re

from .namespaces import EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE
from .schema import InventoryImplementation


KNOWN_KINDS = {EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE}
WELL_96_PATTERN = re.compile(r"^[A-H](?:[1-9]|1[0-2])$")


def validate_item(item: InventoryImplementation) -> None:
    """Validate an inventory object at the item level."""
    kind = str(item.inventory_kind)

    if kind not in KNOWN_KINDS:
        raise ValueError(f"Unknown inventory kind: {kind}")

    if not item.built:
        raise ValueError(f"{item.identity} is missing a built reference")


def validate_well_position(well: str) -> str:
    """Validate and normalize a 96-well plate coordinate (A1-H12)."""
    normalized = well.strip().upper()
    if not WELL_96_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"Invalid 96-well position '{well}'. Expected rows A-H and columns 1-12."
        )
    return normalized
