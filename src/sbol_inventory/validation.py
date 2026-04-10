"""Validation helpers for SBOLInventory."""

from __future__ import annotations

from .namespaces import EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE
from .schema import InventoryImplementation, StorageCollection


KNOWN_KINDS = {EXTRACTED_PLASMID, BACTERIAL_STOCK, SOLID_MEDIA_PLATE}


def validate_item(item: InventoryImplementation) -> None:
    """Validate an inventory object at the item level.

    Every tracked physical inventory object (including solid media plates)
    must be modeled as an :class:`InventoryImplementation` with a known
    ``inventory_kind`` and a SBOL ``built`` reference.
    """
    kind = str(item.inventory_kind)

    if kind not in KNOWN_KINDS:
        raise ValueError(f"Unknown inventory kind: {kind}")

    if not item.built:
        raise ValueError(f"{item.identity} is missing a built reference")


def validate_placement(item: InventoryImplementation, slot: StorageCollection) -> None:
    """Validate whether an implementation is allowed in a slot collection."""
    allowed = {str(kind) for kind in slot.allowed_item_kinds}
    if allowed and str(item.inventory_kind) not in allowed:
        raise ValueError(
            f"{item.identity} of kind {item.inventory_kind} "
            f"is not allowed in slot {slot.identity}"
        )
