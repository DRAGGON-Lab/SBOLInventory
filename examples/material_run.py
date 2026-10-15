"""Synthetic protocol execution, material lineage, evidence, and repository records."""

import sbol3

from sbol_inventory import (
    INSTRUMENT,
    PROCURED_MATERIAL,
    ROOM,
    ExperimentalDataDatabase,
    MetadataDatabase,
    add_all,
    link_evidence,
    make_asset,
    make_document,
    make_evidence,
    make_facility,
    make_material_lot,
    make_zone,
    record_material_derivation,
    record_retrieval,
    record_run,
    record_submission,
    validate_document,
)


def build_material_run() -> sbol3.Document:
    ns = "https://example.org/digital/"
    document = make_document()
    facility = make_facility(ns + "facility")
    room = make_zone(ns + "room", facility=facility, kind=ROOM)
    asset = make_asset(ns + "reader", kind=INSTRUMENT, located_in=room)
    design = sbol3.Component(ns + "design", sbol3.SBO_FUNCTIONAL_ENTITY)
    revised = sbol3.Component(ns + "revised", sbol3.SBO_FUNCTIONAL_ENTITY)
    input_lot = make_material_lot(
        ns + "input_lot", built=design, kind=PROCURED_MATERIAL, located_in=room
    )
    output_lot = make_material_lot(
        ns + "output_lot", built=revised, kind=ns + "PreparedMaterial", located_in=room
    )
    # Instructions and results are placeholder references; this example executes no protocol.
    instructions = sbol3.Attachment(ns + "instructions", source=ns + "files/protocol-v1.json")
    plan = sbol3.Plan(ns + "protocol_v1", attachments=[instructions])
    executor = sbol3.Agent(ns + "operator")
    data, attachment = make_evidence(
        ns + "data",
        attachment_identity=ns + "file",
        source="https://example.org/records/result.csv",
    )
    journal = ExperimentalDataDatabase(ns + "journal", name="Field Journal")
    registry = MetadataDatabase(ns + "registry", name="SynBioHub")
    add_all(document, [facility, room, asset, design, revised, data, attachment, journal, registry])
    add_all(document, [input_lot, output_lot, instructions, plan, executor])
    record_material_derivation(output_lot, [input_lot])
    record_run(
        document,
        ns + "run",
        assets=[asset],
        input_materials=[input_lot],
        output_materials=[output_lot],
        input_components=[design],
        output_components=[revised],
        evidence=[data],
        plan=plan,
        executor=executor,
    )
    link_evidence(data, revised)
    # These calls illustrate records of completed transfers, not actual uploads.
    record_retrieval(design, registry)
    record_submission(revised, registry)
    record_submission(data, journal)
    validate_document(document)
    return document


if __name__ == "__main__":
    print(build_material_run().write_string(sbol3.TURTLE))
