from pathlib import Path
from runpy import run_path

import pytest
import sbol3
from rdflib import Literal, Namespace, URIRef
from rdflib.namespace import RDF

from sbol_inventory import (
    FOR_COMPONENT,
    RETRIEVED_FROM,
    RUN_COMPONENT,
    RUN_INPUT_MATERIAL,
    SUBMITTED_TO,
    ExperimentalDataDatabase,
    InventoryValidationError,
    MetadataDatabase,
    link_evidence,
    make_document,
    record_retrieval,
    record_submission,
    validate_document,
)

NS = "https://example.org/digital/"


def test_components_and_repository_links_survive_round_trip():
    document = run_path(str(Path(__file__).parents[1] / "examples/material_run.py"))[
        "build_material_run"
    ]()
    parsed = make_document()
    parsed.read_string(document.write_string(sbol3.TURTLE), sbol3.TURTLE)
    validate_document(parsed)
    run = parsed.find(NS + "run")
    assert [
        (str(u.entity), list(map(str, u.roles))) for u in run.usage if RUN_COMPONENT in u.roles
    ] == [(NS + "design", [RUN_COMPONENT])]
    design, revised, data = [parsed.find(NS + key) for key in ("design", "revised", "data")]
    assert not design.generated_by
    assert list(revised.generated_by) == [run.identity]
    output_lot = parsed.find(NS + "output_lot")
    assert list(output_lot.generated_by) == [run.identity]
    assert list(output_lot.derived_from_material) == [NS + "input_lot"]
    assert [str(u.entity) for u in run.usage if RUN_INPUT_MATERIAL in u.roles] == [NS + "input_lot"]
    assert list(parsed.find(NS + "protocol_v1").attachments) == [NS + "instructions"]
    # Check native PROV serialization as well as the restored Python objects.
    graph = parsed.graph()
    prov = Namespace("http://www.w3.org/ns/prov#")
    run_iri = URIRef(run.identity)
    association = graph.value(run_iri, prov.qualifiedAssociation)
    assert (association, RDF.type, prov.Association) in graph
    assert (association, prov.hadPlan, URIRef(NS + "protocol_v1")) in graph
    assert (association, prov.agent, URIRef(NS + "operator")) in graph
    assert (URIRef(NS + "protocol_v1"), RDF.type, prov.Plan) in graph
    for output in (revised, output_lot, data):
        assert (URIRef(output.identity), prov.wasGeneratedBy, run_iri) in graph
    assert list(revised.attachments) == list(data.attachments)
    assert data._properties[FOR_COMPONENT] == [URIRef(revised.identity)]
    assert isinstance(parsed.find(NS + "journal"), ExperimentalDataDatabase)
    assert isinstance(parsed.find(NS + "registry"), MetadataDatabase)
    link_evidence(data, revised)
    record_submission(data, parsed.find(NS + "journal"))
    record_retrieval(design, parsed.find(NS + "registry"))
    assert len(data._properties[FOR_COMPONENT]) == 1
    assert len(data._properties[SUBMITTED_TO]) == 1
    assert len(design._properties[RETRIEVED_FROM]) == 1


@pytest.mark.parametrize(
    "predicate,target,rule",
    [
        (FOR_COMPONENT, URIRef(NS + "missing"), "sbolinv-19001"),
        (FOR_COMPONENT, Literal(NS + "revised"), "sbolinv-19001"),
        (SUBMITTED_TO, URIRef(NS + "registry"), "sbolinv-19002"),
        (RETRIEVED_FROM, URIRef(NS + "registry"), "sbolinv-19003"),
    ],
)
def test_invalid_digital_links_are_rejected(predicate, target, rule):
    document = run_path(str(Path(__file__).parents[1] / "examples/material_run.py"))[
        "build_material_run"
    ]()
    document.find(NS + "data")._properties[predicate] = [target]
    with pytest.raises(InventoryValidationError, match=rule):
        validate_document(document)
