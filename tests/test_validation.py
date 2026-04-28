import pytest

from sbol_inventory import (
    BACTERIAL_STOCK,
    BOX,
    DILUTED_PLASMID,
    SOLID_MEDIA_PLATE,
    InventoryImplementation,
    add_all,
    discard_implementation,
    make_bacterial_stock,
    make_box,
    make_diluted_plasmid,
    make_document,
    make_plated_strain,
    make_procured_material,
    make_shelf,
    make_single_well_petri_dish_plate,
    make_solid_96_well_plate,
    make_solid_media_plate,
    move_item,
    place_in_plate,
    place_in_container,
    remove_from_container,
    validate_container_position,
    validate_item,
    validate_placement,
)


def test_validate_item_accepts_new_kinds_with_built():
    item = make_diluted_plasmid(
        uri="https://example.org/implementation/plasmid1",
        plasmid_cd_uri="https://example.org/designs/plasmid1",
    )
    validate_item(item)


def test_box_and_plate_are_inventory_implementations():
    box = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    assert isinstance(box, InventoryImplementation)
    assert isinstance(plate, InventoryImplementation)
    assert str(box.inventory_kind) == BOX
    assert str(plate.inventory_kind) == SOLID_MEDIA_PLATE


def test_validate_placement_storage_rules_for_shelf():
    shelf = make_shelf("https://example.org/storage/4C/shelf1")
    shelf.allowed_item_kinds = [SOLID_MEDIA_PLATE]
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_md",
        rows=["A", "B"],
        columns=[1, 2],
    )
    validate_placement(plate, shelf)


@pytest.mark.parametrize(
    "row,column",
    [("A", 1), ("B", 3)],
)
def test_validate_container_position_accepts_allowed(row, column):
    box = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    assert validate_container_position(box, row=row, column=column) == (row, column)


@pytest.mark.parametrize(
    "row,column",
    [("C", 1), ("A", 99), ("", 1)],
)
def test_validate_container_position_rejects_invalid(row, column):
    box = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    with pytest.raises(ValueError):
        validate_container_position(box, row=row, column=column)


def test_place_in_container_records_reference_and_position():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    plated_strain = make_plated_strain(
        uri="https://example.org/implementation/plated1",
        strain_md_uri="https://example.org/designs/strain_md",
    )

    place_in_container(plate, plated_strain, row="A", column=1)

    assert str(plated_strain.contained_in_container) == str(plate.identity)
    assert str(plated_strain.container_row) == "A"
    assert int(plated_strain.container_column) == 1


def test_duplicate_occupancy_is_rejected_in_same_document():
    doc = make_document()
    box = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    stock = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    procured = make_procured_material(
        uri="https://example.org/implementation/procured1",
        material_md_uri="https://example.org/designs/material1",
    )
    add_all(doc, [box, stock, procured])

    place_in_container(box, stock, row="B", column=2)
    with pytest.raises(ValueError):
        place_in_container(box, procured, row="B", column=2)


def test_move_remove_and_discard_behaviors():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    box = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box_md",
        rows=["A", "B"],
        columns=[1, 2, 3],
    )
    stock = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )

    place_in_container(box, stock, row="A", column=1)
    move_item(stock, plate, row="B", column=3)
    assert str(stock.contained_in_container) == str(plate.identity)
    assert str(stock.container_row) == "B"
    assert int(stock.container_column) == 3

    remove_from_container(stock)
    assert stock.contained_in_container is None
    assert stock.container_row is None
    assert stock.container_column is None

    discard_implementation(stock)
    assert int(stock.is_active) == 0


def test_object_graph_kinds_match_requested_model():
    diluted = make_diluted_plasmid(
        uri="https://example.org/implementation/dp1",
        plasmid_cd_uri="https://example.org/designs/plasmid1",
    )
    stock = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    assert str(diluted.inventory_kind) == DILUTED_PLASMID
    assert str(stock.inventory_kind) == BACTERIAL_STOCK


def test_make_single_well_petri_dish_plate_layout():
    plate = make_single_well_petri_dish_plate(
        uri="https://example.org/implementation/petri1",
        plate_md_uri="https://example.org/designs/petri_md",
    )
    assert list(plate.allowed_rows) == ["A"]
    assert list(plate.allowed_columns) == [1]


def test_make_solid_96_well_plate_layout():
    plate = make_solid_96_well_plate(
        uri="https://example.org/implementation/square96",
        plate_md_uri="https://example.org/designs/square96_md",
    )
    assert list(plate.allowed_rows) == ["A", "B", "C", "D", "E", "F", "G", "H"]
    assert list(plate.allowed_columns) == list(range(1, 13))


@pytest.mark.parametrize("well", ["", "A0", "A13"])
def test_place_in_plate_rejects_malformed_wells(well):
    plate = make_solid_96_well_plate(
        uri="https://example.org/implementation/square96",
        plate_md_uri="https://example.org/designs/square96_md",
    )
    plated_strain = make_plated_strain(
        uri="https://example.org/implementation/plated1",
        strain_md_uri="https://example.org/designs/strain_md",
    )

    with pytest.raises(ValueError):
        place_in_plate(plate, plated_strain, well=well)


def test_place_in_plate_normalizes_well_before_placement():
    plate = make_solid_96_well_plate(
        uri="https://example.org/implementation/square96",
        plate_md_uri="https://example.org/designs/square96_md",
    )
    plated_strain = make_plated_strain(
        uri="https://example.org/implementation/plated1",
        strain_md_uri="https://example.org/designs/strain_md",
    )

    place_in_plate(plate, plated_strain, well=" a1 ")

    assert str(plated_strain.contained_in_container) == str(plate.identity)
    assert str(plated_strain.container_row) == "A"
    assert int(plated_strain.container_column) == 1


def test_place_in_plate_accepts_non_96_container_well_positions():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate384",
        plate_md_uri="https://example.org/designs/plate384_md",
        rows=[chr(x) for x in range(ord("A"), ord("P") + 1)],
        columns=range(1, 25),
    )
    plated_strain = make_plated_strain(
        uri="https://example.org/implementation/plated384",
        strain_md_uri="https://example.org/designs/strain_md",
    )

    place_in_plate(plate, plated_strain, well=" p24 ")

    assert str(plated_strain.contained_in_container) == str(plate.identity)
    assert str(plated_strain.container_row) == "P"
    assert int(plated_strain.container_column) == 24


def test_container_can_list_contained_object_uris():
    doc = make_document()
    plate = make_solid_96_well_plate(
        uri="https://example.org/implementation/square96",
        plate_md_uri="https://example.org/designs/square96_md",
    )
    plated_a1 = make_plated_strain(
        uri="https://example.org/implementation/plated-a1",
        strain_md_uri="https://example.org/designs/strain_md",
    )
    plated_b2 = make_plated_strain(
        uri="https://example.org/implementation/plated-b2",
        strain_md_uri="https://example.org/designs/strain_md",
    )
    add_all(doc, [plate, plated_a1, plated_b2])

    place_in_plate(plate, plated_a1, well="A1")
    place_in_plate(plate, plated_b2, well="B2")

    assert plate.contained_object_uris() == [
        str(plated_a1.identity),
        str(plated_b2.identity),
    ]
