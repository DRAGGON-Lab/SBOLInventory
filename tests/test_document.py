import sbol3

from sbol_inventory import (
    ROOM,
    Facility,
    add_all,
    configure_namespace,
    make_document,
    make_facility,
    make_zone,
    read_document,
    write_rdfxml,
    write_turtle,
)


def test_namespace_and_turtle_document_round_trip(tmp_path):
    previous = sbol3.get_namespace()
    try:
        configure_namespace("https://example.org/catalog")
        document = make_document()
        facility = make_facility("ebef", name="EBEF")
        zone = make_zone("microbiology", facility=facility, kind=ROOM)
        add_all(document, [facility, zone])

        target = write_turtle(document, tmp_path / "facility.ttl")
        parsed = read_document(target)

        assert isinstance(parsed.find(facility.identity), Facility)
        assert str(facility.identity) == "https://example.org/catalog/ebef"
    finally:
        sbol3.set_namespace(previous)


def test_rdfxml_document_round_trip(tmp_path):
    document = make_document()
    facility = make_facility("https://example.org/catalog/facility", name="Facility")
    zone = make_zone(
        "https://example.org/catalog/room",
        facility=facility,
        kind=ROOM,
    )
    add_all(document, [facility, zone])

    target = write_rdfxml(document, tmp_path / "facility.xml")
    parsed = read_document(target, file_format=sbol3.RDF_XML)

    assert isinstance(parsed.find(facility.identity), Facility)
