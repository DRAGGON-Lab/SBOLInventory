"""Facility membership derived from physical containment, never duplicated in RDF."""

from __future__ import annotations

from .schema import Asset, MaterialLot, Zone


def facility_identity(obj: Zone | Asset | MaterialLot) -> str | None:
    """Follow location, or a component asset's physical parent, to a Zone.

    An unlocated object has no known facility. Validation checks dangling
    references, cycles, and consistency between location and composition.
    """
    visited: set[str] = set()
    while obj is not None:
        identity = str(obj.identity)
        if identity in visited:
            return None
        visited.add(identity)
        if isinstance(obj, Zone):
            return str(obj.facility) if obj.facility is not None else None
        if not isinstance(obj, (Asset, MaterialLot)) or obj.document is None:
            return None
        parent = obj.located_in
        if parent is None and isinstance(obj, Asset):
            parent = obj.part_of
        obj = obj.document.find(str(parent)) if parent is not None else None
    return None
