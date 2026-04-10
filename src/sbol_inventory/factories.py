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
from .validation import validate_plate_and_item, validate_well_position


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
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create an extracted plasmid implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = EXTRACTED_PLASMID
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


def make_solid_media_plate(
    uri: str,
    plate_md_uri: str,
    storage_uri: Optional[str] = None,
    design_uri: Optional[str] = None,
) -> InventoryImplementation:
    """Create a solid media plate implementation."""
    x = InventoryImplementation(uri)
    x.inventory_kind = SOLID_MEDIA_PLATE
    x.built = plate_md_uri
    if storage_uri:
        x.stored_at = storage_uri
    if design_uri:
        x.wasDerivedFroms = [design_uri]
    return x


def add_child(parent: StorageCollection, child) -> None:
    """Attach a storage node or inventory item to a parent collection."""
    parent.members.add(child.identity)
    if isinstance(child, StorageCollection):
        child.parent_storage = parent.identity


def place_item(storage: StorageCollection, item: InventoryImplementation) -> None:
    """Place an inventory item into a storage collection."""
    storage.members.add(item.identity)
    item.stored_at = storage.identity


def place_in_plate(
    plate: InventoryImplementation,
    item: InventoryImplementation,
    well: str,
    *,
    check_occupied: bool = True,
) -> None:
    """Place an inventory implementation into a solid media plate well.

    Well coordinates are recorded relative to the plate URI:
    ``item.contained_in_plate = plate.identity`` and ``item.plate_location = 'A1'``.
    """
    validate_plate_and_item(plate, item)
    normalized_well = validate_well_position(well)

    if check_occupied and plate.doc is not None:
        for existing in plate.doc.implementations:
            if not isinstance(existing, InventoryImplementation):
                continue
            if existing.identity == item.identity:
                continue
            if (
                str(existing.contained_in_plate) == str(plate.identity)
                and str(existing.plate_location) == normalized_well
            ):
                raise ValueError(
                    f"Well {normalized_well} in plate {plate.identity} is already occupied by "
                    f"{existing.identity}"
                )

    item.contained_in_plate = plate.identity
    item.plate_location = normalized_well
