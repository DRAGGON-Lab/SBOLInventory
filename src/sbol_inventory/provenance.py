"""Native SBOL 3 and PROV-O records for facility runs and evidence."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

import sbol3

from .namespaces import RUN_ASSET, RUN_INPUT_MATERIAL
from .schema import Asset, MaterialLot


def make_evidence(
    identity: str,
    *,
    attachment_identity: str,
    source: str,
    format_uri: str | None = None,
    size: int | None = None,
    digest: str | None = None,
    digest_algorithm: str | None = None,
    name: str | None = None,
    description: str | None = None,
) -> tuple[sbol3.ExperimentalData, sbol3.Attachment]:
    """Create one ExperimentalData record and its file reference."""

    attachment = sbol3.Attachment(
        identity=attachment_identity,
        source=source,
        format=format_uri,
        size=size,
        hash=digest,
        hash_algorithm=digest_algorithm,
    )
    evidence = sbol3.ExperimentalData(
        identity=identity,
        attachments=[attachment.identity],
        name=name,
        description=description,
    )
    return evidence, attachment


def _require_document_member(document: sbol3.Document, obj: sbol3.TopLevel) -> None:
    resolved = document.find(str(obj.identity))
    if resolved is not obj:
        raise ValueError(f"Add {obj.identity} to the document before recording the run")


def _append_generated_by(obj: sbol3.TopLevel, run_identity: str) -> None:
    generated = [str(value) for value in obj.generated_by]
    if run_identity not in generated:
        obj.generated_by = generated + [run_identity]


def record_material_derivation(
    output: MaterialLot,
    inputs: Sequence[MaterialLot],
) -> None:
    """State which input lots a newly realized output lot derives from.

    A transformed material is a new ``sbol:Implementation``. The prior lot is
    not overwritten, which keeps the run's material history inspectable.
    """

    if output.document is None:
        raise ValueError(f"Add {output.identity} to a document before recording derivation")
    for material in inputs:
        _require_document_member(output.document, material)
        if material is output:
            raise ValueError("A material lot cannot derive from itself")
    existing = [str(value) for value in output.derived_from]
    additions = [str(material.identity) for material in inputs]
    output.derived_from = list(dict.fromkeys([*existing, *additions]))


def record_run(
    document: sbol3.Document,
    identity: str,
    *,
    assets: Sequence[Asset],
    input_materials: Sequence[MaterialLot] = (),
    output_materials: Sequence[MaterialLot] = (),
    evidence: Sequence[sbol3.ExperimentalData] = (),
    plan: sbol3.Plan | None = None,
    executor: sbol3.Agent | None = None,
    start_time: str | datetime | None = None,
    end_time: str | datetime | None = None,
    name: str | None = None,
    description: str | None = None,
) -> sbol3.Activity:
    """Record what a run used and which materials or evidence it generated."""

    if document.find(identity) is not None:
        raise ValueError(f"Document already contains {identity}")
    if (plan is None) != (executor is None):
        raise ValueError("plan and executor must be supplied together")
    related = [*assets, *input_materials, *output_materials, *evidence]
    if plan is not None and executor is not None:
        related.extend([plan, executor])
    for obj in related:
        _require_document_member(document, obj)
    usages = [sbol3.Usage(entity=str(asset.identity), roles=[RUN_ASSET]) for asset in assets]
    usages.extend(
        sbol3.Usage(entity=str(material.identity), roles=[RUN_INPUT_MATERIAL])
        for material in input_materials
    )
    associations = []
    if plan is not None and executor is not None:
        associations.append(
            sbol3.Association(agent=str(executor.identity), plan=str(plan.identity))
        )
    run = sbol3.Activity(
        identity=identity,
        start_time=start_time,
        end_time=end_time,
        usage=usages,
        association=associations,
        name=name,
        description=description,
    )
    document.add(run)
    for obj in [*output_materials, *evidence]:
        _append_generated_by(obj, str(run.identity))
    return run
