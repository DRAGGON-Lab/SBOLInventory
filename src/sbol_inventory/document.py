"""Document-level helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

import sbol2 as sbol
from sbol2 import Config

from .validation import validate_inventory_graph


def configure_synbiohub(identity_namespace: str) -> str:
    """Configure pySBOL2 to mint stable, untyped SynBioHub SBOL URIs.

    ``identity_namespace`` must be the final namespace assigned to a
    submission, for example ``https://synbiohub.org/user/Gon/inventory_2026``.
    Factories must subsequently receive display IDs, not full URIs.
    """
    namespace = identity_namespace.rstrip("/")
    parsed = urlparse(namespace)
    if parsed.scheme != "https" or parsed.netloc != "synbiohub.org" or not parsed.path:
        raise ValueError(
            "identity_namespace must be an https://synbiohub.org submission namespace"
        )

    Config.setHomespace(namespace)
    Config.setOption("sbol_compliant_uris", True)
    Config.setOption("sbol_typed_uris", False)
    return namespace


def make_document() -> sbol.Document:
    """Create an empty SBOL document."""
    return sbol.Document()


def add_all(doc: sbol.Document, objects: Iterable) -> sbol.Document:
    """Add multiple SBOL top-level objects to a document."""
    for obj in objects:
        doc.add(obj)
    return doc


def write_rdfxml(
    doc: sbol.Document,
    path: str | Path,
    *,
    validate: bool = False,
    validate_inventory: bool = True,
) -> Path:
    """Write RDF/XML after local inventory validation.

    Set ``validate=True`` to additionally run pySBOL2's online SBOL validator.
    That network request is deliberately opt-in.
    """
    target = Path(path)
    if validate_inventory:
        validate_inventory_graph(doc)
    previous_validate = Config.getOption("validate")
    Config.setOption("validate", validate)
    try:
        doc.write(str(target))
    finally:
        Config.setOption("validate", previous_validate)
    return target
