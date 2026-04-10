import pytest

from sbol_inventory import (
    InventoryImplementation,
    SOLID_MEDIA_PLATE,
    make_bacterial_stock,
    make_extracted_plasmid,
    make_solid_media_plate,
    place_in_plate,
    validate_item,
    validate_well_position,
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


def test_place_in_plate_records_plate_and_well():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_design1",
    )
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )

    place_in_plate(plate, item, "a1")

    assert str(item.contained_in_plate) == str(plate.identity)
    assert str(item.plate_location) == "A1"


@pytest.mark.parametrize("well", ["A1", "H12"])
def test_validate_well_position_accepts_valid_96_wells(well):
    assert validate_well_position(well) == well


@pytest.mark.parametrize("well", ["A0", "A13", "I1", "Z99"])
def test_validate_well_position_rejects_invalid_96_wells(well):
    with pytest.raises(ValueError):
        validate_well_position(well)


def test_place_in_plate_rejects_non_plate_implementation():
    not_a_plate = make_extracted_plasmid(
        uri="https://example.org/implementation/plasmid1",
        plasmid_cd_uri="https://example.org/designs/plasmid1",
    )
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )

    with pytest.raises(ValueError):
        place_in_plate(not_a_plate, item, "A1")


def test_place_in_plate_duplicate_occupancy_guard_when_in_same_document():
    sbol2 = pytest.importorskip("sbol2")
    doc = sbol2.Document()

    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_design1",
    )
    item1 = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    item2 = make_bacterial_stock(
        uri="https://example.org/implementation/stock2",
        strain_md_uri="https://example.org/designs/strain2",
    )

    for obj in (plate, item1, item2):
        doc.add(obj)

    place_in_plate(plate, item1, "B2")
    with pytest.raises(ValueError):
        place_in_plate(plate, item2, "B2")
