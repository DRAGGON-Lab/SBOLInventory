import pytest

from sbol_inventory import (
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    InventoryImplementation,
    make_bacterial_stock,
    make_extracted_plasmid,
    make_solid_media_plate,
    make_slot,
    place_item,
    validate_item,
    validate_placement,
)


def test_validate_item_accepts_known_kind_with_built():
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    validate_item(item)


def test_validate_placement_accepts_allowed_kind():
    slot = make_slot(
        "https://example.org/storage/-80/shelf1/box1/A1",
        allowed_item_kinds=[BACTERIAL_STOCK],
    )
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    validate_placement(item, slot)


def test_validate_placement_rejects_wrong_kind():
    slot = make_slot(
        "https://example.org/storage/-80/shelf1/box1/A1",
        allowed_item_kinds=[BACTERIAL_STOCK],
    )
    item = make_extracted_plasmid(
        uri="https://example.org/implementation/plasmid1",
        plasmid_cd_uri="https://example.org/designs/plasmid1",
    )
    with pytest.raises(ValueError):
        validate_placement(item, slot)


def test_make_solid_media_plate_returns_inventory_implementation():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate1",
    )
    assert isinstance(plate, InventoryImplementation)
    assert str(plate.inventory_kind) == SOLID_MEDIA_PLATE


def test_solid_media_plate_can_be_placed_in_slot_when_allowed():
    slot = make_slot(
        "https://example.org/storage/4c/shelf1/box1/A1",
        allowed_item_kinds=[SOLID_MEDIA_PLATE],
    )
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate1",
    )
    validate_placement(plate, slot)
    place_item(slot, plate)
    assert str(plate.stored_at) == slot.identity


def test_solid_media_plate_placement_rejected_when_slot_disallows_kind():
    slot = make_slot(
        "https://example.org/storage/4c/shelf1/box1/A1",
        allowed_item_kinds=[BACTERIAL_STOCK],
    )
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate1",
    )
    with pytest.raises(ValueError):
        validate_placement(plate, slot)
