import pytest

from sbol_inventory import (
    BACTERIAL_STOCK,
    BOX,
    DILUTED_PLASMID,
    PLATED_STRAIN,
    SOLID_MEDIA_PLATE,
    InventoryImplementation,
    add_all,
    discard_implementation,
    is_active,
    make_bacterial_stock,
    make_box,
    make_diluted_plasmid,
    make_document,
    make_plated_strain,
    make_procured_material,
    make_solid_media_plate,
    move_to_container,
    place_in_container,
    remove_from_container,
    validate_container_position,
    validate_item,
)


def test_solid_media_plate_and_box_are_inventory_implementations():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    box = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_type1",
    )
    assert isinstance(plate, InventoryImplementation)
    assert isinstance(box, InventoryImplementation)
    assert str(plate.inventory_kind) == SOLID_MEDIA_PLATE
    assert str(box.inventory_kind) == BOX


def test_validate_item_accepts_new_kinds_with_built():
    items = [
        make_diluted_plasmid(
            uri="https://example.org/implementation/plasmid1",
            plasmid_md_uri="https://example.org/designs/plasmid_md_1",
        ),
        make_bacterial_stock(
            uri="https://example.org/implementation/stock1",
            strain_md_uri="https://example.org/designs/strain_md_1",
        ),
        make_procured_material(
            uri="https://example.org/implementation/material1",
            material_md_uri="https://example.org/designs/material_md_1",
        ),
        make_plated_strain(
            uri="https://example.org/implementation/plated1",
            strain_md_uri="https://example.org/designs/strain_md_2",
        ),
    ]
    for item in items:
        validate_item(item)


def test_validate_container_position_accepts_valid_values():
    container = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_type1",
        allowed_rows=["A", "B"],
        allowed_columns=[1, 2, 3],
    )
    row, column = validate_container_position(container, "a", 2)
    assert row == "A"
    assert column == 2


@pytest.mark.parametrize(
    "row,column",
    [("I", 1), ("A", 0), ("A", 13), ("Z", 99)],
)
def test_place_in_container_rejects_invalid_positions(row, column):
    container = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_type1",
        allowed_rows=["A", "B"],
        allowed_columns=[1, 2, 3],
    )
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain_md_1",
    )
    with pytest.raises(ValueError):
        place_in_container(container, item, row, column)


def test_place_in_container_records_reference_and_position():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    item = make_plated_strain(
        uri="https://example.org/implementation/plated1",
        strain_md_uri="https://example.org/designs/strain_md_1",
    )

    place_in_container(plate, item, "H", 12)

    assert str(item.contained_in_implementation) == str(plate.identity)
    assert str(item.container_row) == "H"
    assert int(item.container_column) == 12


def test_duplicate_occupancy_rejected_in_same_document():
    doc = make_document()
    box = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_type1",
    )
    item1 = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain_md_1",
    )
    item2 = make_procured_material(
        uri="https://example.org/implementation/material1",
        material_md_uri="https://example.org/designs/material_md_1",
    )
    add_all(doc, [box, item1, item2])

    place_in_container(box, item1, "A", 1)
    with pytest.raises(ValueError):
        place_in_container(box, item2, "A", 1)


def test_move_remove_and_discard_workflow():
    box1 = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_type1",
    )
    box2 = make_box(
        uri="https://example.org/implementation/box2",
        box_md_uri="https://example.org/designs/box_type1",
    )
    item = make_diluted_plasmid(
        uri="https://example.org/implementation/plasmid1",
        plasmid_md_uri="https://example.org/designs/plasmid_md_1",
    )

    place_in_container(box1, item, "B", 2)
    move_to_container(item, box2, "C", 3)

    assert str(item.contained_in_implementation) == str(box2.identity)
    assert str(item.container_row) == "C"
    assert int(item.container_column) == 3

    remove_from_container(box2, item)
    assert item.contained_in_implementation is None

    assert is_active(item)
    discard_implementation(item)
    assert not is_active(item)


def test_kind_constants_still_accessible():
    assert BACTERIAL_STOCK
    assert DILUTED_PLASMID
    assert PLATED_STRAIN
