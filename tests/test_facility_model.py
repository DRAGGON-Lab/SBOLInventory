import pytest
import sbol3

from sbol_inventory import (
    ABSORBANCE_MEASUREMENT,
    CONTAINMENT_ZONE,
    CONTROL_API,
    CONTROL_MANUAL,
    FUNCTIONAL_UNIT,
    INSTRUMENT,
    LIQUID_TRANSFER,
    QUALIFICATION_EXECUTABLE,
    QUALIFICATION_PLANNABLE,
    QUALIFICATION_QUALIFIED,
    ROOM,
    THERMAL_CYCLING,
    Asset,
    Facility,
    InventoryValidationError,
    PropertyValue,
    Zone,
    add_all,
    find_qualified_assets,
    make_asset,
    make_capability,
    make_document,
    make_facility,
    make_property,
    make_zone,
    validate_document,
)

NS = "https://example.org/ebef/"


def test_ebef_shape_round_trips_as_typed_sbol3_extensions():
    document = make_document()
    ebef = make_facility(NS + "facility", name="EBEF")
    microbiology = make_zone(
        NS + "microbiology",
        facility=ebef,
        kind=ROOM,
        name="Microbiology floor",
    )
    chamber_interior = make_zone(
        NS + "anaerobic_chamber_1_interior",
        facility=ebef,
        parent_zone=microbiology,
        kind=CONTAINMENT_ZONE,
        name="Anaerobic chamber 1 interior",
    )
    chamber = make_asset(
        NS + "anaerobic_chamber_1",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microbiology,
        establishes_zones=[chamber_interior],
        manufacturer="Coy",
        model="Vinyl anaerobic chamber",
    )
    prep = make_asset(
        NS + "microlab_prep_1",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=chamber_interior,
        manufacturer="Hamilton",
        model="Microlab Prep",
        capabilities=[
            make_capability(
                LIQUID_TRANSFER,
                qualification=QUALIFICATION_EXECUTABLE,
                control_mode=CONTROL_API,
                parameters=[
                    make_property(
                        "https://example.org/property/channel_count",
                        8,
                    )
                ],
            )
        ],
    )
    proflex = make_asset(
        NS + "proflex_1",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microbiology,
        manufacturer="Thermo Fisher Scientific",
        model="ProFlex",
    )
    blocks = [
        make_asset(
            NS + f"proflex_1_block_{index}",
            facility=ebef,
            kind=FUNCTIONAL_UNIT,
            part_of=proflex,
            capabilities=[
                make_capability(
                    THERMAL_CYCLING,
                    qualification=QUALIFICATION_PLANNABLE,
                    control_mode=CONTROL_MANUAL,
                )
            ],
        )
        for index in range(1, 4)
    ]
    add_all(document, [ebef, microbiology, chamber_interior, chamber, prep, proflex, *blocks])

    validate_document(document)
    turtle = document.write_string(sbol3.TURTLE)

    parsed = make_document()
    parsed.read_string(turtle, sbol3.TURTLE)
    validate_document(parsed)

    parsed_prep = parsed.find(prep.identity)
    assert isinstance(parsed.find(ebef.identity), Facility)
    assert isinstance(parsed.find(chamber_interior.identity), Zone)
    assert isinstance(parsed_prep, Asset)
    assert str(parsed_prep.located_in) == str(chamber_interior.identity)
    assert str(parsed_prep.capabilities[0].kind) == LIQUID_TRANSFER
    assert int(parsed_prep.capabilities[0].parameters[0].integer_value) == 8


def test_qualified_asset_query_is_deterministic_and_respects_maturity():
    document = make_document()
    facility = make_facility(NS + "facility")
    room = make_zone(NS + "room", facility=facility, kind=ROOM)
    planned = make_asset(
        NS + "planned",
        facility=facility,
        kind=INSTRUMENT,
        located_in=room,
        capabilities=[
            make_capability(
                ABSORBANCE_MEASUREMENT,
                qualification=QUALIFICATION_PLANNABLE,
            )
        ],
    )
    qualified = make_asset(
        NS + "qualified",
        facility=facility,
        kind=INSTRUMENT,
        located_in=room,
        capabilities=[
            make_capability(
                ABSORBANCE_MEASUREMENT,
                qualification=QUALIFICATION_QUALIFIED,
            )
        ],
    )
    add_all(document, [facility, room, qualified, planned])
    validate_document(document)

    matches = find_qualified_assets(
        document,
        ABSORBANCE_MEASUREMENT,
        minimum_qualification=QUALIFICATION_EXECUTABLE,
    )
    assert [str(match.asset.identity) for match in matches] == [str(qualified.identity)]

    all_matches = find_qualified_assets(
        document,
        ABSORBANCE_MEASUREMENT,
        minimum_qualification=QUALIFICATION_PLANNABLE,
    )
    assert [str(match.asset.identity) for match in all_matches] == [
        str(planned.identity),
        str(qualified.identity),
    ]
    filtered_matches = find_qualified_assets(
        document,
        ABSORBANCE_MEASUREMENT,
        minimum_qualification=QUALIFICATION_PLANNABLE,
        facility=str(facility.identity),
    )
    assert filtered_matches == all_matches


def test_candidate_query_respects_effective_activity_through_all_containment_edges():
    document = make_document()
    facility = make_facility(NS + "facility")
    building = make_zone(NS + "building", facility=facility, kind=ROOM)
    room = make_zone(
        NS + "room",
        facility=facility,
        kind=ROOM,
        parent_zone=building,
    )
    container = make_asset(
        NS + "container",
        facility=facility,
        kind=INSTRUMENT,
        located_in=room,
    )
    parent = make_asset(
        NS + "parent",
        facility=facility,
        kind=INSTRUMENT,
    )
    child = make_asset(
        NS + "child",
        facility=facility,
        kind=FUNCTIONAL_UNIT,
        located_in=container,
        part_of=parent,
        capabilities=[
            make_capability(
                ABSORBANCE_MEASUREMENT,
                qualification=QUALIFICATION_PLANNABLE,
            )
        ],
    )
    add_all(document, [facility, building, room, container, parent, child])
    validate_document(document)

    def matches():
        return find_qualified_assets(document, ABSORBANCE_MEASUREMENT)

    assert [match.asset for match in matches()] == [child]

    building.is_active = False
    assert matches() == []
    building.is_active = True

    container.is_active = False
    assert matches() == []
    container.is_active = True

    parent.is_active = False
    assert matches() == []


def test_candidate_query_rejects_unknown_qualification_with_stable_rule_id():
    document = make_document()
    with pytest.raises(ValueError, match=r"\[sbolinv-18001\]"):
        find_qualified_assets(
            document,
            ABSORBANCE_MEASUREMENT,
            minimum_qualification="https://example.org/UnknownQualification",
        )
    with pytest.raises(ValueError, match=r"\[sbolinv-18002\]"):
        find_qualified_assets(document, "relative-capability-kind")


def test_zone_and_asset_cycles_are_rejected():
    document = make_document()
    facility = make_facility(NS + "facility")
    zone_a = make_zone(NS + "zone_a", facility=facility, kind=ROOM)
    zone_b = make_zone(NS + "zone_b", facility=facility, kind=ROOM, parent_zone=zone_a)
    zone_a.parent_zone = zone_b.identity
    add_all(document, [facility, zone_a, zone_b])

    with pytest.raises(InventoryValidationError, match="Zone hierarchy contains a cycle"):
        validate_document(document)


def test_mixed_asset_composition_and_location_cycle_is_rejected():
    document = make_document()
    facility = make_facility(NS + "facility")
    parent = make_asset(NS + "parent", facility=facility, kind=INSTRUMENT)
    child = make_asset(
        NS + "child",
        facility=facility,
        kind=FUNCTIONAL_UNIT,
        part_of=parent,
    )
    parent.located_in = child.identity
    add_all(document, [facility, parent, child])

    with pytest.raises(InventoryValidationError, match="Asset containment contains a cycle"):
        validate_document(document)


def test_duplicate_capability_requires_a_child_functional_unit():
    document = make_document()
    facility = make_facility(NS + "facility")
    asset = make_asset(
        NS + "cycler",
        facility=facility,
        kind=INSTRUMENT,
        capabilities=[
            make_capability(THERMAL_CYCLING),
            make_capability(THERMAL_CYCLING),
        ],
    )
    add_all(document, [facility, asset])

    with pytest.raises(InventoryValidationError, match="use a child asset"):
        validate_document(document)


def test_cross_facility_location_is_rejected():
    document = make_document()
    first = make_facility(NS + "first_facility")
    second = make_facility(NS + "second_facility")
    second_room = make_zone(NS + "second_room", facility=second, kind=ROOM)
    misplaced = make_asset(
        NS + "misplaced",
        facility=first,
        kind=INSTRUMENT,
        located_in=second_room,
    )
    add_all(document, [first, second, second_room, misplaced])

    with pytest.raises(InventoryValidationError, match="different facilities"):
        validate_document(document)


def test_unknown_qualification_and_ambiguous_property_value_are_rejected():
    document = make_document()
    facility = make_facility(NS + "facility")
    ambiguous = PropertyValue(
        kind="https://example.org/property/value",
        text_value="eight",
        integer_value=8,
    )
    capability = make_capability(
        LIQUID_TRANSFER,
        qualification="https://example.org/qualification/untested",
        parameters=[ambiguous],
    )
    asset = make_asset(
        NS + "handler",
        facility=facility,
        kind=INSTRUMENT,
        capabilities=[capability],
    )
    add_all(document, [facility, asset])

    with pytest.raises(InventoryValidationError, match="unknown qualification"):
        validate_document(document)

    capability.qualification = QUALIFICATION_PLANNABLE
    with pytest.raises(InventoryValidationError, match="exactly one typed value"):
        validate_document(document)

    ambiguous.integer_value = None
    asset.kind = "instrument"
    with pytest.raises(InventoryValidationError, match="must be an absolute IRI"):
        validate_document(document)
