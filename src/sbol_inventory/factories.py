"""Factory functions for storage nodes and inventory implementations."""

from __future__ import annotations

from typing import Optional

from .namespaces import (
    EXTRACTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    FRIDGE_MINUS_80,
    FRIDGE_MINUS_20,
    FRIDGE_4C,
    SHELF,
    BOX,
)
from .schema import InventoryImplementation, StorageCollection
from .validation import validate_well_position


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


def make_extracted_plasmid(
    uri: str,
    plasmid_cd_uri: str,
    stored_at_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create an extracted plasmid implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = EXTRACTED_PLASMID
    x.built = plasmid_cd_uri
    if stored_at_uri:
        x.stored_at = stored_at_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def make_bacterial_stock(
    uri: str,
    strain_md_uri: str,
    stored_at_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a bacterial stock implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = BACTERIAL_STOCK
    x.built = strain_md_uri
    if stored_at_uri:
        x.stored_at = stored_at_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def make_solid_media_plate(
    uri: str,
    plate_md_uri: str,
    stored_at_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a solid media plate implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = SOLID_MEDIA_PLATE
    x.built = plate_md_uri
    if stored_at_uri:
        x.stored_at = stored_at_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def add_child(parent: StorageCollection, child) -> None:
    """Attach a storage node or inventory item to a parent collection."""
    parent.members.add(child.identity)
    if isinstance(child, StorageCollection):
        child.parent_storage = parent.identity


def _iter_implementations(doc):
    implementations = getattr(doc, "implementations", None)
    if implementations is None:
        return []
    if hasattr(implementations, "values"):
        return implementations.values()
    return implementations


def place_in_plate(
    plate: InventoryImplementation,
    item: InventoryImplementation,
    well: str,
) -> None:
    """Place an inventory implementation into a 96-well solid media plate."""
    if not isinstance(plate, InventoryImplementation):
        raise TypeError("plate must be an InventoryImplementation")
    if str(plate.inventory_kind) != SOLID_MEDIA_PLATE:
        raise ValueError("plate must be an InventoryImplementation of kind SolidMediaPlate")

    if not isinstance(item, InventoryImplementation):
        raise TypeError("item must be an InventoryImplementation")

    normalized_well = validate_well_position(well)

    if plate.doc is not None and plate.doc is item.doc:
        for existing in _iter_implementations(plate.doc):
            if existing.identity == item.identity:
                continue
            if not isinstance(existing, InventoryImplementation):
                continue
            if str(existing.contained_in_plate) == str(plate.identity) and str(existing.plate_location) == normalized_well:
                raise ValueError(
                    f"Well {normalized_well} in plate {plate.identity} is already occupied by {existing.identity}"
                )

    item.contained_in_plate = plate.identity
    item.plate_location = normalized_well
