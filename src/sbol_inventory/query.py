"""Deterministic catalog queries used by planners and control planes."""

from __future__ import annotations

from dataclasses import dataclass

import sbol3

from .namespaces import QUALIFICATION_ORDER, QUALIFICATION_PLANNABLE
from .schema import Asset, Capability, Facility, MaterialLot, Zone


@dataclass(frozen=True)
class CapabilityMatch:
    """One qualified asset and the offering that satisfied a capability query."""

    asset: Asset
    capability: Capability


def facilities(document: sbol3.Document) -> list[Facility]:
    return sorted(
        (obj for obj in document.objects if isinstance(obj, Facility)),
        key=lambda obj: str(obj.identity),
    )


def zones(document: sbol3.Document, facility: Facility | None = None) -> list[Zone]:
    facility_identity = str(facility.identity) if facility is not None else None
    return sorted(
        (
            obj
            for obj in document.objects
            if isinstance(obj, Zone)
            and (facility_identity is None or str(obj.facility) == facility_identity)
        ),
        key=lambda obj: str(obj.identity),
    )


def assets(document: sbol3.Document, facility: Facility | None = None) -> list[Asset]:
    facility_identity = str(facility.identity) if facility is not None else None
    return sorted(
        (
            obj
            for obj in document.objects
            if isinstance(obj, Asset)
            and (facility_identity is None or str(obj.facility) == facility_identity)
        ),
        key=lambda obj: str(obj.identity),
    )


def material_lots(document: sbol3.Document, facility: Facility | None = None) -> list[MaterialLot]:
    facility_identity = str(facility.identity) if facility is not None else None
    return sorted(
        (
            obj
            for obj in document.objects
            if isinstance(obj, MaterialLot)
            and obj.inventory_kind is not None
            and (facility_identity is None or str(obj.facility) == facility_identity)
        ),
        key=lambda obj: str(obj.identity),
    )


def qualification_rank(qualification: str) -> int:
    try:
        return QUALIFICATION_ORDER.index(str(qualification))
    except ValueError as error:
        raise ValueError(f"Unknown qualification {qualification}") from error


def find_qualified_assets(
    document: sbol3.Document,
    capability_kind: str,
    *,
    minimum_qualification: str = QUALIFICATION_PLANNABLE,
    facility: Facility | None = None,
) -> list[CapabilityMatch]:
    """Find active offerings at or above a required qualification level."""

    required_rank = qualification_rank(minimum_qualification)
    matches: list[CapabilityMatch] = []
    for asset in assets(document, facility):
        if asset.is_active is not True:
            continue
        for capability in asset.capabilities:
            if capability.is_active is not True or str(capability.kind) != capability_kind:
                continue
            if qualification_rank(str(capability.qualification)) < required_rank:
                continue
            matches.append(CapabilityMatch(asset=asset, capability=capability))
    return matches
