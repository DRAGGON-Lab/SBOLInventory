"""Document-level helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import sbol2 as sbol


def make_document() -> sbol.Document:
    """Create an empty SBOL document."""
    return sbol.Document()


def add_all(doc: sbol.Document, objects: Iterable) -> sbol.Document:
    """Add multiple SBOL top-level objects to a document."""
    for obj in objects:
        doc.add(obj)
    return doc


def write_rdfxml(doc: sbol.Document, path: str | Path) -> Path:
    """Write a document as RDF/XML."""
    target = Path(path)
    doc.write(str(target))
    return target
