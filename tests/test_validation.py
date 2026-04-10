import pytest

from sbol_inventory import (
    SOLID_MEDIA_PLATE,
    InventoryImplementation,
    make_bacterial_stock,
    make_document,
    make_solid_media_plate,
    validate_item,
    validate_well_position,
    place_in_plate,
)


def test_validate_item_accepts_known_kind_with_built():
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    validate_item(item)


def test_solid_media_plate_is_inventory_implementation():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_design1",
    )
    assert isinstance(plate, InventoryImplementation)
    assert str(plate.inventory_kind) == SOLID_MEDIA_PLATE


@pytest.mark.parametrize("well", ["A1", "H12", "a1"])
def test_validate_well_position_accepts_valid_96_wells(well):
    assert validate_well_position(well) in {"A1", "H12"}


@pytest.mark.parametrize("well", ["A0", "A13", "I1", "Z99"])
def test_validate_well_position_rejects_invalid_96_wells(well):
    with pytest.raises(ValueError):
        validate_well_position(well)


def test_place_in_plate_records_plate_and_well():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_design1",
    )
    sample = make_bacterial_stock(
        uri="https://example.org/implementation/sample1",
        strain_md_uri="https://example.org/designs/strain1",
    )

    normalized_well = place_in_plate(plate, sample, "a1")

    assert normalized_well == "A1"
    assert str(sample.contained_in_plate) == str(plate.identity)
    assert str(sample.plate_location) == "A1"


def test_place_in_plate_rejects_non_inventory_item():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_design1",
    )

    with pytest.raises(TypeError):
        place_in_plate(plate, "not-an-item", "A1")


def test_place_in_plate_rejects_duplicate_occupancy_when_in_document():
    doc = make_document()
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_design1",
    )
    item_1 = make_bacterial_stock(
        uri="https://example.org/implementation/sample1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    item_2 = make_bacterial_stock(
        uri="https://example.org/implementation/sample2",
        strain_md_uri="https://example.org/designs/strain2",
    )
    for obj in [plate, item_1, item_2]:
        doc.add(obj)

    place_in_plate(plate, item_1, "A1")

    with pytest.raises(ValueError):
        place_in_plate(plate, item_2, "A1")
