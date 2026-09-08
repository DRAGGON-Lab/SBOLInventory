"""Physical custody, design use and generation, and recorded repository transfers."""

import sbol3

from sbol_inventory import (
    INSTRUMENT,
    ROOM,
    ExperimentalDataDatabase,
    MetadataDatabase,
    add_all,
    link_evidence,
    make_asset,
    make_document,
    make_evidence,
    make_facility,
    make_zone,
    record_retrieval,
    record_run,
    record_submission,
    validate_document,
)


def build_material_run():
    ns = "https://example.org/digital/"
    document = make_document()
    facility = make_facility(ns + "facility")
    room = make_zone(ns + "room", facility=facility, kind=ROOM)
    asset = make_asset(ns + "reader", kind=INSTRUMENT, located_in=room)
    design = sbol3.Component(ns + "design", sbol3.SBO_FUNCTIONAL_ENTITY)
    revised = sbol3.Component(ns + "revised", sbol3.SBO_FUNCTIONAL_ENTITY)
    data, attachment = make_evidence(
        ns + "data",
        attachment_identity=ns + "file",
        source="https://example.org/records/result.csv",
    )
    journal = ExperimentalDataDatabase(ns + "journal", name="Field Journal")
    registry = MetadataDatabase(ns + "registry", name="SynBioHub")
    add_all(document, [facility, room, asset, design, revised, data, attachment, journal, registry])
    record_run(
        document,
        ns + "run",
        assets=[asset],
        input_components=[design],
        output_components=[revised],
        evidence=[data],
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
