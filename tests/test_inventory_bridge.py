from pathlib import Path

import pytest
from sbol2 import Config

from sbol_inventory import (
    add_all,
    add_child,
    configure_synbiohub,
    make_bacterial_stock,
    make_box,
    make_document,
    make_fridge_4c,
    make_shelf,
    make_solid_media_plate,
    place_in_container,
    validate_inventory_graph,
    write_rdfxml,
)


def _restore_config(options):
    for option, value in options.items():
        Config.setOption(option, value)


def test_configure_synbiohub_generates_canonical_untyped_uris():
    options = {
        option: Config.getOption(option)
        for option in ("homespace", "sbol_compliant_uris", "sbol_typed_uris")
    }
    try:
        configure_synbiohub("https://synbiohub.org/user/Gon/inventory_2026/")
        fridge = make_fridge_4c("fridge_4c")

        assert str(fridge.identity) == (
            "https://synbiohub.org/user/Gon/inventory_2026/fridge_4c/1"
        )
        assert str(fridge.persistentIdentity) == (
            "https://synbiohub.org/user/Gon/inventory_2026/fridge_4c"
        )
        assert fridge.displayId == "fridge_4c"
    finally:
        _restore_config(options)


def test_configure_synbiohub_rejects_full_uris_as_factory_identifiers():
    options = {
        option: Config.getOption(option)
        for option in ("homespace", "sbol_compliant_uris", "sbol_typed_uris")
    }
    try:
        configure_synbiohub("https://synbiohub.org/user/Gon/inventory_2026")
        with pytest.raises(ValueError, match="do not pass a full URI"):
            make_fridge_4c("https://synbiohub.org/user/Gon/inventory_2026/fridge/1")
    finally:
        _restore_config(options)


@pytest.mark.parametrize(
    "namespace",
    [
        "http://synbiohub.org/user/Gon/inventory",
        "https://api.synbiohub.org/user/Gon/inventory",
        "https://example.org/user/Gon/inventory",
    ],
)
def test_configure_synbiohub_rejects_noncanonical_identity_namespaces(namespace):
    with pytest.raises(ValueError):
        configure_synbiohub(namespace)


def test_design_provenance_is_serialized(tmp_path):
    doc = make_document()
    box = make_box(
        "box",
        "https://example.org/designs/box",
        ["A"],
        [1],
        design_uri="https://example.org/designs/original",
    )
    add_all(doc, [box])

    output = write_rdfxml(doc, tmp_path / "inventory.xml")

    assert "https://example.org/designs/original" in output.read_text()
    assert list(box.wasDerivedFrom) == ["https://example.org/designs/original"]


def test_hierarchy_enforces_temperature_policy_and_validates_graph():
    doc = make_document()
    fridge = make_fridge_4c("fridge")
    shelf = make_shelf("shelf")
    plate = make_solid_media_plate("plate", "https://example.org/designs/plate", ["A"], [1])
    stock = make_bacterial_stock("stock", "https://example.org/designs/stock")
    box = make_box("box", "https://example.org/designs/box", ["A"], [1])
    add_all(doc, [fridge, shelf, plate, stock, box])

    add_child(fridge, shelf)
    add_child(shelf, plate)
    with pytest.raises(ValueError, match="not allowed"):
        add_child(shelf, box)

    place_in_container(plate, stock, "A", 1)
    validate_inventory_graph(doc)

    assert stock.stored_at is None
    assert str(stock.identity) not in {str(member) for member in shelf.members}


def test_reparenting_removes_old_direct_membership():
    doc = make_document()
    fridge = make_fridge_4c("fridge")
    shelf_a = make_shelf("shelf_a")
    shelf_b = make_shelf("shelf_b")
    plate = make_solid_media_plate("plate", "https://example.org/designs/plate", ["A"], [1])
    add_all(doc, [fridge, shelf_a, shelf_b, plate])

    add_child(fridge, shelf_a)
    add_child(fridge, shelf_b)
    add_child(shelf_a, plate)
    add_child(shelf_b, plate)

    assert str(plate.identity) not in {str(member) for member in shelf_a.members}
    assert str(plate.identity) in {str(member) for member in shelf_b.members}
    validate_inventory_graph(doc)


def test_container_mutations_require_a_shared_document():
    plate = make_solid_media_plate("plate", "https://example.org/designs/plate", ["A"], [1])
    stock = make_bacterial_stock("stock", "https://example.org/designs/stock")

    with pytest.raises(ValueError, match="one document"):
        place_in_container(plate, stock, "A", 1)


def test_duplicate_slot_is_rejected_after_document_addition():
    doc = make_document()
    box = make_box("box", "https://example.org/designs/box", ["A"], [1])
    stock_a = make_bacterial_stock("stock_a", "https://example.org/designs/stock_a")
    stock_b = make_bacterial_stock("stock_b", "https://example.org/designs/stock_b")
    add_all(doc, [box, stock_a, stock_b])

    place_in_container(box, stock_a, "A", 1)
    with pytest.raises(ValueError, match="occupied"):
        place_in_container(box, stock_b, "A", 1)


def test_write_rdfxml_does_not_change_global_validation_setting(tmp_path):
    previous_validate = Config.getOption("validate")
    Config.setOption("validate", True)
    try:
        doc = make_document()
        add_all(doc, [make_fridge_4c("fridge")])
        target = Path(tmp_path / "inventory.xml")

        write_rdfxml(doc, target)

        assert target.exists()
        assert Config.getOption("validate") is True
    finally:
        Config.setOption("validate", previous_validate)


def test_write_rdfxml_rejects_a_graph_with_inconsistent_inverse_location(tmp_path):
    doc = make_document()
    shelf = make_shelf("shelf")
    plate = make_solid_media_plate("plate", "https://example.org/designs/plate", ["A"], [1])
    add_all(doc, [shelf, plate])
    # Deliberately bypass the mutation API to model malformed imported data.
    shelf.members = [plate.identity]

    with pytest.raises(ValueError, match="Inverse storage link"):
        write_rdfxml(doc, tmp_path / "invalid.xml")
