import pytest

from sbol_inventory import (
    BACTERIAL_STOCK,
    make_bacterial_stock,
    make_extracted_plasmid,
    make_slot,
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
