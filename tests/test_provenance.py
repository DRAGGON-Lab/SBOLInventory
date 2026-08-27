import pytest
import sbol3

from sbol_inventory import (
    INSTRUMENT,
    ROOM,
    RUN_ASSET,
    RUN_INPUT_MATERIAL,
    add_all,
    make_asset,
    make_bacterial_stock,
    make_document,
    make_evidence,
    make_facility,
    make_zone,
    record_material_derivation,
    record_run,
    validate_document,
)

NS = "https://example.org/run/"


def test_run_records_assets_inputs_outputs_and_evidence():
    document = make_document()
    facility = make_facility(NS + "facility")
    room = make_zone(NS + "room", facility=facility, kind=ROOM)
    reader = make_asset(
        NS + "reader",
        facility=facility,
        kind=INSTRUMENT,
        located_in=room,
    )
    input_design = sbol3.Component(NS + "input_design", sbol3.SBO_FUNCTIONAL_ENTITY)
    output_design = sbol3.Component(NS + "output_design", sbol3.SBO_FUNCTIONAL_ENTITY)
    input_lot = make_bacterial_stock(
        NS + "input",
        built=input_design,
        facility=facility,
    )
    output_lot = make_bacterial_stock(
        NS + "output",
        built=output_design,
        facility=facility,
    )
    evidence, attachment = make_evidence(
        NS + "growth_curve",
        attachment_identity=NS + "growth_curve_csv",
        source="https://example.org/results/growth-curve.csv",
        format_uri="https://edamontology.org/format_3752",
    )
    plan = sbol3.Plan(NS + "reviewed_plan")
    executor = sbol3.Agent(NS + "operator")
    add_all(
        document,
        [
            facility,
            room,
            reader,
            input_design,
            output_design,
            input_lot,
            output_lot,
            evidence,
            attachment,
            plan,
            executor,
        ],
    )

    record_material_derivation(output_lot, [input_lot])

    run = record_run(
        document,
        NS + "run_1",
        assets=[reader],
        input_materials=[input_lot],
        output_materials=[output_lot],
        evidence=[evidence],
        plan=plan,
        executor=executor,
    )
    validate_document(document)

    roles = {str(role) for usage in run.usage for role in usage.roles}
    assert roles == {RUN_ASSET, RUN_INPUT_MATERIAL}
    assert list(output_lot.generated_by) == [run.identity]
    assert list(output_lot.derived_from) == [input_lot.identity]
    assert list(evidence.generated_by) == [run.identity]
    assert str(run.association[0].agent) == str(executor.identity)
    assert str(run.association[0].plan) == str(plan.identity)

    with pytest.raises(ValueError, match="plan and executor"):
        record_run(
            document,
            NS + "run_without_executor",
            assets=[reader],
            plan=plan,
        )
