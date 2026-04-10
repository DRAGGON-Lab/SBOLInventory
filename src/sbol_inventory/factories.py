"""Factory functions for storage nodes and inventory implementations."""

from __future__ import annotations

from typing import Optional, Sequence

from .namespaces import (
    EXTRACTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    FRIDGE_MINUS_80,
    FRIDGE_MINUS_20,
    FRIDGE_4C,
    SHELF,
    BOX,
    SLOT,
)
from .schema import InventoryImplementation, StorageCollection


def make_fridge_minus80(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_MINUS_80
    x.temperature_c = -80
    x.allowed_item_kinds = [BACTERIAL_STOCK]
    return x


def make_fridge_minus20(uri: str) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = FRIDGE_MINUS_20
    x.temperature_c = -20
    x.allowed_item_kinds = [EXTRACTED_PLASMID]
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


def make_box(uri: str, label: Optional[str] = None) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = BOX
    if label:
        x.label = label
    return x


def make_slot(
    uri: str,
    label: Optional[str] = None,
    row: Optional[str] = None,
    column: Optional[str] = None,
    allowed_item_kinds: Optional[Sequence[str]] = None,
) -> StorageCollection:
    x = StorageCollection(uri)
    x.storage_kind = SLOT
    if label:
        x.label = label
    if row:
        x.row = row
    if column:
        x.column = column
    if allowed_item_kinds:
        x.allowed_item_kinds = list(allowed_item_kinds)
    return x


def make_extracted_plasmid(
    uri: str,
    plasmid_cd_uri: str,
    slot_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create an extracted plasmid implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = EXTRACTED_PLASMID
    x.built = plasmid_cd_uri
    if slot_uri:
        x.stored_at = slot_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def make_bacterial_stock(
    uri: str,
    strain_md_uri: str,
    slot_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a bacterial stock implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = BACTERIAL_STOCK
    x.built = strain_md_uri
    if slot_uri:
        x.stored_at = slot_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def make_solid_media_plate(
    uri: str,
    plate_md_uri: str,
    slot_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a solid media plate as a physical inventory implementation.

    A plate is represented as an ``InventoryImplementation`` (not a storage
    ``Collection``). It may reference a design object through ``built`` and can
    be placed into a storage slot like other inventory items.
    """
    x = InventoryImplementation(uri)
    x.inventory_kind = SOLID_MEDIA_PLATE
    x.built = plate_md_uri
    if slot_uri:
        x.stored_at = slot_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def add_child(parent: StorageCollection, child) -> None:
    """Attach a storage node or inventory item to a parent collection."""
    if hasattr(parent.members, "add"):
        parent.members.add(child.identity)
    else:
        parent.members.append(child.identity)
    if isinstance(child, StorageCollection):
        child.parent_storage = parent.identity


def place_item(slot: StorageCollection, item: InventoryImplementation) -> None:
    """Place an inventory item into a leaf slot."""
    if hasattr(slot.members, "add"):
        slot.members.add(item.identity)
    else:
        slot.members.append(item.identity)
    item.stored_at = slot.identity
