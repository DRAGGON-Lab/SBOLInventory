"""Links between designs, experimental evidence, and repository records.

These helpers record facts after a consumer completes a transfer. They do not
perform network requests or claim that a transfer has succeeded.
"""

import sbol3
from rdflib import URIRef

from .namespaces import (
    EXPERIMENTAL_DATA_DATABASE,
    FOR_COMPONENT,
    METADATA_DATABASE,
    RETRIEVED_FROM,
    SUBMITTED_TO,
)


class ExperimentalDataDatabase(sbol3.CustomTopLevel):
    """A repository for experimental data, such as Field Journal."""

    def __init__(
        self, identity, *, name=None, description=None, type_uri=EXPERIMENTAL_DATA_DATABASE
    ):
        super().__init__(identity=identity, type_uri=type_uri, name=name, description=description)


class MetadataDatabase(sbol3.CustomTopLevel):
    """A repository for SBOL designs, such as SynBioHub."""

    def __init__(self, identity, *, name=None, description=None, type_uri=METADATA_DATABASE):
        super().__init__(identity=identity, type_uri=type_uri, name=name, description=description)


def _require_members(*objects):
    document = objects[0].document
    if document is None or any(document.find(str(obj.identity)) is not obj for obj in objects):
        raise ValueError("Add all linked objects to the same document first")


def _link(subject, predicate, target):
    values = subject._properties[predicate]
    value = URIRef(str(target.identity))
    if value not in values:
        values.append(value)


def link_evidence(evidence: sbol3.ExperimentalData, component: sbol3.Component) -> None:
    """Associate data with a design and attach the same evidence files to it."""
    if not isinstance(evidence, sbol3.ExperimentalData) or not isinstance(
        component, sbol3.Component
    ):
        raise TypeError("Evidence must be ExperimentalData and its subject a Component")
    _require_members(evidence, component)
    _link(evidence, FOR_COMPONENT, component)
    component.attachments = list(
        dict.fromkeys(str(value) for value in [*component.attachments, *evidence.attachments])
    )


def record_submission(
    record: sbol3.ExperimentalData | sbol3.Component,
    database: ExperimentalDataDatabase | MetadataDatabase,
) -> None:
    """Record the repository to which this data or design was submitted."""
    if not (
        isinstance(record, sbol3.ExperimentalData)
        and isinstance(database, ExperimentalDataDatabase)
        or isinstance(record, sbol3.Component)
        and isinstance(database, MetadataDatabase)
    ):
        raise TypeError(
            "ExperimentalData requires a data database; Component requires a metadata database"
        )
    _require_members(record, database)
    _link(record, SUBMITTED_TO, database)


def record_retrieval(component: sbol3.Component, database: MetadataDatabase) -> None:
    """Record the repository from which a Component was retrieved."""
    if not isinstance(component, sbol3.Component) or not isinstance(database, MetadataDatabase):
        raise TypeError("Retrieval links a Component to a metadata database")
    _require_members(component, database)
    _link(component, RETRIEVED_FROM, database)


sbol3.Document.register_builder(EXPERIMENTAL_DATA_DATABASE, ExperimentalDataDatabase)
sbol3.Document.register_builder(METADATA_DATABASE, MetadataDatabase)
