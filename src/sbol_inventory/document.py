"""Document lifecycle helpers for the SBOL 3 facility profile."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from urllib.parse import urlparse

import sbol3

from .schema import register_extensions
from .validation import validate_document


def configure_namespace(identity_namespace: str | None) -> str | None:
    """Set the default SBOL 3 namespace used for display-ID construction."""

    if identity_namespace is None:
        sbol3.set_namespace(None)
        return None
    namespace = identity_namespace.rstrip("/")
    parsed = urlparse(namespace)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("identity_namespace must be an absolute HTTP(S) IRI")
    sbol3.set_namespace(namespace)
    return namespace


def configure_synbiohub(identity_namespace: str) -> str:
    """Compatibility helper for a canonical SynBioHub collection namespace."""

    namespace = identity_namespace.rstrip("/")
    parsed = urlparse(namespace)
    if parsed.scheme != "https" or parsed.netloc != "synbiohub.org" or not parsed.path:
        raise ValueError("identity_namespace must be an https://synbiohub.org collection namespace")
    configure_namespace(namespace)
    return namespace


def make_document() -> sbol3.Document:
    register_extensions()
    return sbol3.Document()


def add_all(document: sbol3.Document, objects: Iterable[sbol3.TopLevel]) -> sbol3.Document:
    document.add(list(objects))
    return document


def read_document(
    path: str | Path,
    *,
    file_format: str | None = None,
    validate: bool = True,
) -> sbol3.Document:
    register_extensions()
    document = sbol3.Document()
    document.read(path, file_format)
    if validate:
        validate_document(document)
    return document


def write_document(
    document: sbol3.Document,
    path: str | Path,
    *,
    file_format: str | None = None,
    validate: bool = True,
) -> Path:
    target = Path(path)
    if validate:
        validate_document(document)
    document.write(target, file_format)
    return target


def write_rdfxml(
    document: sbol3.Document,
    path: str | Path,
    *,
    validate: bool = True,
) -> Path:
    return write_document(
        document,
        path,
        file_format=sbol3.RDF_XML,
        validate=validate,
    )


def write_turtle(
    document: sbol3.Document,
    path: str | Path,
    *,
    validate: bool = True,
) -> Path:
    return write_document(
        document,
        path,
        file_format=sbol3.TURTLE,
        validate=validate,
    )
