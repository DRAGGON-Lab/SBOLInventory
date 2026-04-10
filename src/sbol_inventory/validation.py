"""Validation helpers for SBOLInventory."""

from __future__ import annotations

import re

from .namespaces import EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE
from .schema import InventoryImplementation, StorageCollection


KNOWN_KINDS = {EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE}
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


def validate_plate_and_item(plate: InventoryImplementation, item: InventoryImplementation) -> None:
    """Validate types for plate placement semantics."""
    if not isinstance(plate, InventoryImplementation):
        raise ValueError("Plate must be an InventoryImplementation")
    if not isinstance(item, InventoryImplementation):
        raise ValueError("Item must be an InventoryImplementation")

    if str(plate.inventory_kind) != SOLID_MEDIA_PLATE:
        raise ValueError(
            f"Plate {plate.identity} must have inventory kind SolidMediaPlate"
        )
