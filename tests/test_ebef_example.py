from pathlib import Path
from runpy import run_path

import sbol3

from sbol_inventory import (
    ABSORBANCE_MEASUREMENT,
    COLD_STORAGE,
    CONTROL_UNSPECIFIED,
    INCUBATION,
    LIQUID_HANDLING,
    QUALIFICATION_DESCRIBED,
    QUALIFICATION_PLANNABLE,
    SHAKING_INCUBATION,
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


def test_serialized_catalog_distinguishes_heating_limits_and_measurement_operations():
    document = make_document()
    document.read_string(build_catalog().write_string(sbol3.TURTLE), sbol3.TURTLE)
    ns = "https://example.org/ebef/"
    om = "http://www.ontology-of-units-of-measure.org/resource/om-2/"
    epoch = document.find(ns + "biotek_epoch_2")
    capabilities = {str(capability.kind): capability for capability in epoch.capabilities}
    assert set(capabilities) == {ABSORBANCE_MEASUREMENT, INCUBATION}
    limits = {
        str(parameter.kind).removeprefix(ns + "property/"): parameter
        for parameter in capabilities[INCUBATION].parameters
    }
    assert limits["minimum_temperature"].real_value == 18.0
    assert str(limits["minimum_temperature"].unit) == om + "degreeCelsius"
    assert limits["maximum_temperature"].real_value == 65.0
    offset = limits["minimum_temperature_above_ambient"]
    assert offset.real_value == 4.0
    assert str(offset.unit) == om + "kelvin"
    assert str(offset.derived_from[0]).startswith("https://www.agilent.com/")

    heating = document.find(ns + "eppendorf_s44i_1").capabilities[0]
    assert str(heating.kind) == SHAKING_INCUBATION
    parameters = {str(parameter.kind): parameter for parameter in heating.parameters}
    assert parameters[ns + "property/supports_refrigeration"].boolean_value is False


def test_room_summary_does_not_become_a_reservable_cold_storage_asset():
    document = build_catalog()
    assert document.find("https://example.org/ebef/freezer_room") is not None
    assert document.find("https://example.org/ebef/cold_storage_group") is None
    assert find_qualified_assets(document, COLD_STORAGE) == []
