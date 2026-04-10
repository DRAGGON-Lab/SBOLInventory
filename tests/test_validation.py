import pytest

from sbol_inventory import (
    SOLID_MEDIA_PLATE,
    InventoryImplementation,
    make_bacterial_stock,
    make_box,
    make_extracted_plasmid,
    make_solid_media_plate,
    place_in_plate,
    validate_item,
    validate_placement,
    validate_well_position,
)


def test_validate_item_accepts_known_kind_with_built():
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    validate_item(item)


def test_validate_placement_accepts_allowed_kind():
    box = make_box("https://example.org/storage/-80/shelf1/box1")
    box.allowed_item_kinds = [SOLID_MEDIA_PLATE]
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    validate_placement(plate, box)


def test_validate_placement_rejects_wrong_kind():
    box = make_box("https://example.org/storage/-80/shelf1/box1")
    box.allowed_item_kinds = [SOLID_MEDIA_PLATE]
    item = make_extracted_plasmid(
        uri="https://example.org/implementation/plasmid1",
        plasmid_cd_uri="https://example.org/designs/plasmid1",
    )
    with pytest.raises(ValueError):
        validate_placement(item, box)


def test_solid_media_plate_is_inventory_implementation():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    assert isinstance(plate, InventoryImplementation)
    assert str(plate.inventory_kind) == SOLID_MEDIA_PLATE


def test_validate_well_position_accepts_boundaries():
    assert validate_well_position("A1") == "A1"
    assert validate_well_position("h12") == "H12"


@pytest.mark.parametrize("well", ["A0", "A13", "I1", "Z99"])
def test_validate_well_position_rejects_invalid_values(well):
    with pytest.raises(ValueError):
        validate_well_position(well)


def test_place_in_plate_records_plate_reference_and_well():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )

    place_in_plate(plate, item, "A1")

    assert str(item.contained_in_plate) == str(plate.identity)
    assert str(item.plate_location) == "A1"


def test_place_in_plate_rejects_non_plate_target():
    not_a_plate = make_bacterial_stock(
        uri="https://example.org/implementation/notplate",
        strain_md_uri="https://example.org/designs/strain1",
    )
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain2",
    )

    with pytest.raises(ValueError):
        place_in_plate(not_a_plate, item, "A1")


def test_place_in_plate_rejects_duplicate_occupancy_when_in_same_document():
    from sbol_inventory import make_document, add_all

    doc = make_document()
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    item1 = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    item2 = make_bacterial_stock(
        uri="https://example.org/implementation/stock2",
        strain_md_uri="https://example.org/designs/strain2",
    )
    add_all(doc, [plate, item1, item2])

    place_in_plate(plate, item1, "H12")

    with pytest.raises(ValueError):
        place_in_plate(plate, item2, "H12")
