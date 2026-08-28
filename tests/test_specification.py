from pathlib import Path

import pytest
import sbol3
from pyshacl import validate as validate_shacl
from rdflib import Graph, Namespace, URIRef
from rdflib.compare import isomorphic
from rdflib.namespace import RDF

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - exercised on Python 3.10
    import tomli as tomllib

from sbol_inventory import (
    QUERY_RULE_IDS,
    RULE_IDS,
    VALIDATOR_RULE_IDS,
    InventoryValidationError,
    make_document,
    namespaces,
    validate_inventory_graph,
)
from sbol_inventory.schema import Asset, Capability, Facility, MaterialLot, PropertyValue, Zone

REPOSITORY = Path(__file__).resolve().parents[1]
SPECIFICATION = REPOSITORY / "spec" / "0.2"
FIXTURES = SPECIFICATION / "fixtures"


def _load_toml(path: Path) -> dict:
    with path.open("rb") as stream:
        return tomllib.load(stream)


RULE_CATALOG = _load_toml(SPECIFICATION / "rules.toml")
FIXTURE_MANIFEST = _load_toml(FIXTURES / "manifest.toml")
SHAPES = Graph().parse(SPECIFICATION / "shapes.ttl")
VOCABULARY = Graph().parse(SPECIFICATION / "vocabulary.ttl")
SBOL = Namespace("http://sbols.org/v3#")
PROV = Namespace("http://www.w3.org/ns/prov#")


def _shacl_result(graph: Graph) -> tuple[bool, str]:
    conforms, _, report = validate_shacl(
        graph,
        shacl_graph=SHAPES,
        ont_graph=VOCABULARY,
        inference="none",
    )
    return bool(conforms), str(report)


def _read_python_document(path: Path) -> sbol3.Document:
    document = make_document()
    document.read(path, sbol3.TURTLE)
    return document


def test_normative_rdf_artifacts_parse_and_shapes_pass_meta_shacl():
    assert len(VOCABULARY) > 0
    assert len(SHAPES) > 0
    conforms, _, report = validate_shacl(Graph(), shacl_graph=SHAPES, meta_shacl=True)
    assert conforms, report


def test_rule_catalog_matches_python_ids_shapes_and_fixtures():
    rules = RULE_CATALOG["rules"]
    ids = [rule["id"] for rule in rules]
    assert len(ids) == len(set(ids))
    assert set(ids) == RULE_IDS
    assert {rule["id"] for rule in rules if "Validator" in rule["classes"]} == VALIDATOR_RULE_IDS
    assert {rule["id"] for rule in rules if "Query" in rule["classes"]} == QUERY_RULE_IDS

    serialized_shapes = SHAPES.serialize(format="turtle")
    for rule in rules:
        if rule["shacl_core"]:
            assert rule["id"] in serialized_shapes
        if "Validator" in rule["classes"] and rule["id"] != "sbolinv-10001":
            assert "fixture" in rule
            assert (SPECIFICATION / rule["fixture"]).is_file()

    listed_paths = {fixture["path"] for fixture in FIXTURE_MANIFEST["fixtures"]}
    actual_paths = {
        str(path.relative_to(FIXTURES))
        for directory in (FIXTURES / "valid", FIXTURES / "invalid")
        for path in directory.glob("*.ttl")
    }
    assert listed_paths == actual_paths

    rules_by_fixture = {
        rule["fixture"].removeprefix("fixtures/"): rule["id"] for rule in rules if "fixture" in rule
    }
    rules_by_id = {rule["id"]: rule for rule in rules}
    for fixture in FIXTURE_MANIFEST["fixtures"]:
        if fixture["expect"] == "invalid":
            assert rules_by_fixture[fixture["path"]] == fixture["rule"]
            assert fixture["shacl"] is rules_by_id[fixture["rule"]]["shacl_core"]


def test_python_profile_terms_are_declared_and_capacity_group_is_not_defined():
    declared = {str(subject) for subject in VOCABULARY.subjects() if isinstance(subject, URIRef)}
    namespace_terms = {
        value
        for name, value in vars(namespaces).items()
        if name.isupper()
        and isinstance(value, str)
        and name not in {"EX", "PROFILE_VERSION"}
        and not name.endswith("_NS")
    }
    schema_terms = {
        value
        for cls in (Facility, Zone, Asset, Capability, PropertyValue, MaterialLot)
        for name, value in vars(cls).items()
        if (name == "TYPE_URI" or name.endswith("_URI")) and isinstance(value, str)
    }
    assert not (namespace_terms | schema_terms) - declared
    assert "https://sbol.io/ns/facility#capacityGroup" not in declared
    assert not hasattr(Capability, "CAPACITY_GROUP_URI")


@pytest.mark.parametrize(
    "fixture",
    [fixture for fixture in FIXTURE_MANIFEST["fixtures"] if fixture["expect"] == "valid"],
    ids=lambda fixture: Path(fixture["path"]).stem,
)
def test_valid_fixture_conformance_and_round_trip(fixture: dict):
    path = FIXTURES / fixture["path"]
    source_graph = Graph().parse(path)
    conforms, report = _shacl_result(source_graph)
    assert conforms, report

    document = _read_python_document(path)
    core_report = document.validate()
    assert not core_report.errors, core_report
    validate_inventory_graph(document)

    serialized = document.write_string(sbol3.TURTLE)
    round_trip_graph = Graph().parse(data=serialized, format="turtle")
    assert isomorphic(source_graph, round_trip_graph)


def test_valid_fixtures_use_valid_sbol_terms_and_implementation_provenance():
    valid_fixtures = [
        fixture for fixture in FIXTURE_MANIFEST["fixtures"] if fixture["expect"] == "valid"
    ]
    for fixture in valid_fixtures:
        graph = Graph().parse(FIXTURES / fixture["path"])
        assert not list(graph.triples((None, SBOL.attachment, None)))
        for implementation in graph.subjects(RDF.type, SBOL.Implementation):
            for source in graph.objects(implementation, PROV.wasDerivedFrom):
                assert (source, RDF.type, SBOL.Component) in graph


@pytest.mark.parametrize(
    "fixture",
    [fixture for fixture in FIXTURE_MANIFEST["fixtures"] if fixture["expect"] == "invalid"],
    ids=lambda fixture: Path(fixture["path"]).stem,
)
def test_invalid_fixture_reports_expected_rule(fixture: dict):
    path = FIXTURES / fixture["path"]
    source_graph = Graph().parse(path)
    conforms, report = _shacl_result(source_graph)
    if fixture["shacl"]:
        assert not conforms
        assert fixture["rule"] in report
    else:
        assert conforms, report

    if fixture["python_semantic"]:
        document = _read_python_document(path)
        with pytest.raises(InventoryValidationError) as error:
            validate_inventory_graph(document)
        assert error.value.rule_id == fixture["rule"]
