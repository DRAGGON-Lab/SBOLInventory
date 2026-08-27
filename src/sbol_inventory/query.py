"""Deterministic catalog queries used by planners and control planes."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import sbol3

from .namespaces import QUALIFICATION_ORDER, QUALIFICATION_PLANNABLE
from .rules import QUERY_ELIGIBILITY_RULE, QUERY_QUALIFICATION_RULE
from .schema import Asset, Capability, Facility, MaterialLot, Zone


@dataclass(frozen=True)
class CapabilityMatch:
    """One qualified asset and the offering that satisfied a capability query."""

    asset: Asset
    capability: Capability


FacilityFilter = Facility | str | None


def _facility_filter_identity(facility: FacilityFilter) -> str | None:
    if isinstance(facility, Facility):
        return str(facility.identity)
    return str(facility) if facility is not None else None


def facilities(document: sbol3.Document) -> list[Facility]:
    return sorted(
        (obj for obj in document.objects if isinstance(obj, Facility)),
        key=lambda obj: str(obj.identity),
    )


def zones(document: sbol3.Document, facility: FacilityFilter = None) -> list[Zone]:
    facility_identity = _facility_filter_identity(facility)
    return sorted(
        (
            obj
            for obj in document.objects
            if isinstance(obj, Zone)
            and (facility_identity is None or str(obj.facility) == facility_identity)
        ),
        key=lambda obj: str(obj.identity),
    )


def assets(document: sbol3.Document, facility: FacilityFilter = None) -> list[Asset]:
    facility_identity = _facility_filter_identity(facility)
    return sorted(
        (
            obj
            for obj in document.objects
            if isinstance(obj, Asset)
            and (facility_identity is None or str(obj.facility) == facility_identity)
        ),
        key=lambda obj: str(obj.identity),
    )


def material_lots(document: sbol3.Document, facility: FacilityFilter = None) -> list[MaterialLot]:
    facility_identity = _facility_filter_identity(facility)
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
        raise ValueError(
            f"[{QUERY_QUALIFICATION_RULE}] Unknown qualification {qualification}"
        ) from error


def _require_capability_kind(capability_kind: str) -> str:
    text = str(capability_kind)
    parsed = urlparse(text)
    if (
        not parsed.scheme
        or any(character.isspace() for character in text)
        or (parsed.scheme in {"http", "https"} and not parsed.netloc)
    ):
        raise ValueError(
            f"[{QUERY_ELIGIBILITY_RULE}] Capability kind must be an absolute IRI, found {text!r}"
        )
    return text


def _is_effectively_active(document: sbol3.Document, asset: Asset) -> bool:
    visited_assets: set[str] = set()
    visited_zones: set[str] = set()

    def zone_is_active(zone: Zone) -> bool:
        identity = str(zone.identity)
        if identity in visited_zones:
            return True
        visited_zones.add(identity)
        if zone.is_active is not True:
            return False
        if zone.parent_zone is None:
            return True
        parent = document.find(str(zone.parent_zone))
        return isinstance(parent, Zone) and zone_is_active(parent)

    def asset_is_active(candidate: Asset) -> bool:
        identity = str(candidate.identity)
        if identity in visited_assets:
            return True
        visited_assets.add(identity)
        if candidate.is_active is not True:
            return False
        if candidate.part_of is not None:
            parent_asset = document.find(str(candidate.part_of))
            if not isinstance(parent_asset, Asset) or not asset_is_active(parent_asset):
                return False
        if candidate.located_in is not None:
            location = document.find(str(candidate.located_in))
            if isinstance(location, Asset):
                return asset_is_active(location)
            if isinstance(location, Zone):
                return zone_is_active(location)
            return False
        return True

    return asset_is_active(asset)


def find_qualified_assets(
    document: sbol3.Document,
    capability_kind: str,
    *,
    minimum_qualification: str = QUALIFICATION_PLANNABLE,
    facility: FacilityFilter = None,
) -> list[CapabilityMatch]:
    """Find active offerings at or above a required qualification level."""

    requested_kind = _require_capability_kind(capability_kind)
    required_rank = qualification_rank(minimum_qualification)
    matches: list[CapabilityMatch] = []
    for asset in assets(document, facility):
        if not _is_effectively_active(document, asset):
            continue
        for capability in asset.capabilities:
            if capability.is_active is not True or str(capability.kind) != requested_kind:
                continue
            if qualification_rank(str(capability.qualification)) < required_rank:
                continue
            matches.append(CapabilityMatch(asset=asset, capability=capability))
    return sorted(matches, key=lambda match: str(match.asset.identity))
