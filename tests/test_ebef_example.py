from pathlib import Path
from runpy import run_path

import sbol3

from sbol_inventory import (
    CONTROL_UNSPECIFIED,
    LIQUID_HANDLING,
    QUALIFICATION_DESCRIBED,
    QUALIFICATION_PLANNABLE,
    THERMAL_CYCLING,
    Asset,
    Facility,
    Zone,
    find_qualified_assets,
    make_document,
    validate_document,
)


def build_catalog():
    example = Path(__file__).parents[1] / "examples" / "ebef_catalog.py"
    return run_path(str(example))["build_ebef_catalog"]()


def test_public_ebef_catalog_is_valid_and_spatially_typed():
    document = build_catalog()
    validate_document(document)

    serialized = document.write_string(sbol3.TURTLE)
    parsed = make_document()
    parsed.read_string(serialized, sbol3.TURTLE)
    validate_document(parsed)

    assert isinstance(parsed.find("https://example.org/ebef/facility"), Facility)
    chamber = parsed.find("https://example.org/ebef/anaerobic_chamber_1")
    interior = parsed.find("https://example.org/ebef/anaerobic_chamber_1_interior")
    prep = parsed.find("https://example.org/ebef/microlab_prep")
    assert isinstance(chamber, Asset)
    assert isinstance(interior, Zone)
    assert isinstance(prep, Asset)
    assert str(chamber.establishes_zones[0]) == str(interior.identity)
    assert str(prep.located_in) == str(interior.identity)


def test_public_facts_are_described_candidates_not_execution_claims():
    document = build_catalog()

    thermal = find_qualified_assets(
        document,
        THERMAL_CYCLING,
        minimum_qualification=QUALIFICATION_DESCRIBED,
    )
    liquid = find_qualified_assets(
        document,
        LIQUID_HANDLING,
        minimum_qualification=QUALIFICATION_DESCRIBED,
    )
    executable = find_qualified_assets(
        document,
        LIQUID_HANDLING,
        minimum_qualification=QUALIFICATION_PLANNABLE,
    )

    assert len(thermal) == 3
    assert len(liquid) == 1
    assert str(liquid[0].capability.control_mode) == CONTROL_UNSPECIFIED
    assert executable == []
