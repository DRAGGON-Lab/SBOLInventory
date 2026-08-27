from datetime import datetime, timezone

import pytest
import sbol3

from sbol_inventory import (
    BACTERIAL_STOCK,
    ROOM,
    Asset,
    InventoryValidationError,
    MaterialLot,
    add_all,
    discard,
    make_bacterial_stock,
    make_box,
    make_document,
    make_facility,
    make_shelf,
    make_zone,
    move_item,
    place_in_container,
    validate_document,
)

NS = "https://example.org/inventory/"


def make_inventory():
    document = make_document()
    facility = make_facility(NS + "facility")
    room = make_zone(NS + "room", facility=facility, kind=ROOM)
    fridge = Asset(
        NS + "freezer",
        facility=facility,
        kind="https://draggon.org/ns/inventory#FridgeMinus80C",
        located_in=room,
        is_active=True,
    )
    shelf = make_shelf(
        NS + "shelf",
        facility=facility,
        part_of=fridge,
        allowed_positions=["BOX-1", "BOX-2"],
    )
    box_a = make_box(
        NS + "box_a",
        facility=facility,
        located_in=shelf,
        position="BOX-1",
        rows=["A", "B"],
        columns=[1, 2],
    )
    box_b = make_box(
        NS + "box_b",
        facility=facility,
        located_in=shelf,
        position="BOX-2",
        rows=["A", "B"],
        columns=[1, 2],
    )
    strain = sbol3.Component(NS + "strain_design", sbol3.SBO_FUNCTIONAL_ENTITY)
    lot = make_bacterial_stock(
        NS + "stock_1",
        built=strain,
        facility=facility,
        barcode="stock-1",
    )
    add_all(document, [facility, room, fridge, shelf, box_a, box_b, strain, lot])
    return document, facility, box_a, box_b, lot


def test_material_lot_remains_a_native_sbol_implementation():
    document, _, box_a, _, lot = make_inventory()
    place_in_container(box_a, lot, "A", 1)
    validate_document(document)

    assert isinstance(lot, sbol3.Implementation)
    assert isinstance(lot, MaterialLot)
    assert str(lot.inventory_kind) == BACTERIAL_STOCK
    assert str(lot.located_in) == str(box_a.identity)
    assert str(lot.position) == "A1"


def test_material_metadata_round_trips_with_native_rdf_types():
    document, _, _, _, lot = make_inventory()
    lot.freeze_date = datetime(2026, 8, 26, 12, 30, tzinfo=timezone.utc)

    serialized = document.write_string(sbol3.TURTLE)
    parsed = make_document()
    parsed.read_string(serialized, sbol3.TURTLE)
    validate_document(parsed)

    parsed_lot = parsed.find(lot.identity)
    assert isinstance(parsed_lot, MaterialLot)
    assert parsed_lot.freeze_date == datetime(2026, 8, 26, 12, 30, tzinfo=timezone.utc)


def test_occupancy_move_and_lifecycle_invariants_are_preserved():
    document, facility, box_a, box_b, lot = make_inventory()
    second_design = sbol3.Component(NS + "strain_design_2", sbol3.SBO_FUNCTIONAL_ENTITY)
    second = make_bacterial_stock(
        NS + "stock_2",
        built=second_design,
        facility=facility,
    )
    add_all(document, [second_design, second])
    place_in_container(box_a, lot, "A", 1)

    with pytest.raises(ValueError, match="occupied"):
        place_in_container(box_a, second, "A", 1)

    with pytest.raises(ValueError, match="not allowed"):
        place_in_container(box_a, second, "Z", 99, check_occupied=False)

    move_item(lot, box_b, "B", 2)
    discard(lot)
    validate_document(document)
    assert str(lot.located_in) == str(box_b.identity)
    assert str(lot.position) == "B2"
    assert lot.is_active is False


def test_material_lot_requires_a_resolvable_component_design():
    document, _, _, _, lot = make_inventory()
    lot.built = "https://example.org/missing_design"

    with pytest.raises(InventoryValidationError, match="built reference"):
        validate_document(document)


def test_generic_sbol_implementation_is_not_forced_into_inventory_profile():
    document = make_document()
    design = sbol3.Component(NS + "design", sbol3.SBO_DNA)
    implementation = sbol3.Implementation(NS + "implementation", built=design)
    add_all(document, [design, implementation])

    validate_document(document)

    serialized = document.write_string(sbol3.TURTLE)
    parsed = make_document()
    parsed.read_string(serialized, sbol3.TURTLE)
    validate_document(parsed)

    parsed_implementation = parsed.find(implementation.identity)
    assert isinstance(parsed_implementation, MaterialLot)
    assert parsed_implementation.inventory_kind is None
    assert parsed_implementation.is_active is None
