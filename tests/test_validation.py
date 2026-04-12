import pytest

from sbol_inventory import (
    BOX,
    BACTERIAL_STOCK,
    DILUTED_PLASMID,
    PROCURED_MATERIAL,
    SOLID_MEDIA_PLATE,
    InventoryImplementation,
    add_all,
    add_child,
    discard_implementation,
    make_bacterial_stock,
    make_box,
    make_diluted_plasmid,
    make_document,
    make_fridge_4c,
    make_fridge_minus20,
    make_fridge_minus80,
    make_plated_strain,
    make_procured_material,
    make_shelf,
    make_solid_media_plate,
    move_item,
    place_in_container,
    remove_from_container,
    validate_container_slot,
    validate_item,
    validate_placement,
)


def test_graph_fridge4c_shelf_plate_plated_strain():
    doc = make_document()
    fridge = make_fridge_4c("https://example.org/storage/4C")
    shelf = make_shelf("https://example.org/storage/4C/shelf1")
    plate = make_solid_media_plate(
        uri="https://example.org/impl/plate1",
        plate_md_uri="https://example.org/md/plate1",
        allowed_rows=["A", "B"],
        allowed_columns=[1, 2],
    )
    plated = make_plated_strain(
        uri="https://example.org/impl/plated1",
        strain_md_uri="https://example.org/md/strain1",
    )

    add_all(doc, [fridge, shelf, plate, plated])
    add_child(fridge, shelf)
    add_child(shelf, plate)
    place_in_container(plate, plated, "A", 1)

    assert str(plate.inventory_kind) == SOLID_MEDIA_PLATE
    assert str(plated.contained_in_implementation) == str(plate.identity)
    assert str(plated.location_row) == "A"
    assert int(plated.location_column) == 1


def test_graph_minus80_shelf_box_items():
    doc = make_document()
    freezer = make_fridge_minus80("https://example.org/storage/-80")
    shelf = make_shelf("https://example.org/storage/-80/shelf1")
    box = make_box(
        uri="https://example.org/impl/box80",
        box_md_uri="https://example.org/md/box80",
        allowed_rows=["A"],
        allowed_columns=[1, 2],
    )
    stock = make_bacterial_stock(
        uri="https://example.org/impl/stock1",
        strain_md_uri="https://example.org/md/strain1",
    )
    procured = make_procured_material(
        uri="https://example.org/impl/procured1",
        material_md_uri="https://example.org/md/procured1",
    )

    add_all(doc, [freezer, shelf, box, stock, procured])
    add_child(freezer, shelf)
    add_child(shelf, box)
    place_in_container(box, stock, "A", 1)
    place_in_container(box, procured, "A", 2)

    assert str(box.inventory_kind) == BOX
    assert str(stock.inventory_kind) == BACTERIAL_STOCK
    assert str(procured.inventory_kind) == PROCURED_MATERIAL


def test_graph_minus20_shelf_box_items_with_diluted_plasmid():
    doc = make_document()
    freezer = make_fridge_minus20("https://example.org/storage/-20")
    shelf = make_shelf("https://example.org/storage/-20/shelf1")
    box = make_box(
        uri="https://example.org/impl/box20",
        box_md_uri="https://example.org/md/box20",
        allowed_rows=["A"],
        allowed_columns=[1, 2],
    )
    plasmid = make_diluted_plasmid(
        uri="https://example.org/impl/plasmid1",
        plasmid_cd_uri="https://example.org/md/plasmid1",
    )
    procured = make_procured_material(
        uri="https://example.org/impl/procured2",
        material_md_uri="https://example.org/md/procured2",
    )

    add_all(doc, [freezer, shelf, box, plasmid, procured])
    add_child(freezer, shelf)
    add_child(shelf, box)
    place_in_container(box, plasmid, "A", 1)
    place_in_container(box, procured, "A", 2)

    assert str(plasmid.inventory_kind) == DILUTED_PLASMID


def test_validate_item_accepts_known_kind_with_built():
    item = make_bacterial_stock(
        uri="https://example.org/implementation/stock1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    validate_item(item)


def test_validate_placement_accepts_allowed_kind():
    shelf = make_shelf("https://example.org/storage/4c/shelf1")
    shelf.allowed_item_kinds = [SOLID_MEDIA_PLATE]
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    validate_placement(plate, shelf)


def test_solid_media_plate_is_inventory_implementation():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
    )
    assert isinstance(plate, InventoryImplementation)
    assert str(plate.inventory_kind) == SOLID_MEDIA_PLATE


def test_validate_container_slot_accepts_values():
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
        allowed_rows=["A", "H"],
        allowed_columns=[1, 12],
    )
    assert validate_container_slot(plate, "a", 1) == ("A", 1)


@pytest.mark.parametrize("row,column", [("Z", 1), ("A", 13), ("A", 0)])
def test_validate_container_slot_rejects_invalid_values(row, column):
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
        allowed_rows=["A", "H"],
        allowed_columns=[1, 12],
    )
    with pytest.raises(ValueError):
        validate_container_slot(plate, row, column)


def test_place_in_container_rejects_duplicate_occupancy_when_in_same_document():
    doc = make_document()
    plate = make_solid_media_plate(
        uri="https://example.org/implementation/plate1",
        plate_md_uri="https://example.org/designs/plate_type1",
        allowed_rows=["A"],
        allowed_columns=[1],
    )
    item1 = make_plated_strain(
        uri="https://example.org/implementation/item1",
        strain_md_uri="https://example.org/designs/strain1",
    )
    item2 = make_plated_strain(
        uri="https://example.org/implementation/item2",
        strain_md_uri="https://example.org/designs/strain2",
    )
    add_all(doc, [plate, item1, item2])

    place_in_container(plate, item1, "A", 1)

    with pytest.raises(ValueError):
        place_in_container(plate, item2, "A", 1)


def test_move_and_remove_and_discard():
    doc = make_document()
    box1 = make_box(
        uri="https://example.org/implementation/box1",
        box_md_uri="https://example.org/designs/box1",
        allowed_rows=["A"],
        allowed_columns=[1, 2],
    )
    box2 = make_box(
        uri="https://example.org/implementation/box2",
        box_md_uri="https://example.org/designs/box2",
        allowed_rows=["B"],
        allowed_columns=[1],
    )
    item = make_procured_material(
        uri="https://example.org/implementation/procured1",
        material_md_uri="https://example.org/designs/material1",
    )
    add_all(doc, [box1, box2, item])

    place_in_container(box1, item, "A", 2)
    move_item(item, box2, "B", 1)
    assert str(item.contained_in_implementation) == str(box2.identity)
    assert str(item.location_row) == "B"
    assert int(item.location_column) == 1

    remove_from_container(box2, item)
    assert item.contained_in_implementation is None

    discard_implementation(item)
    assert bool(item.active) is False
