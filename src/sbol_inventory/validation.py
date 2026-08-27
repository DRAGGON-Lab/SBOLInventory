"""Semantic validation beyond the SBOL 3 core rules."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar
from urllib.parse import urlparse

import sbol3

from .namespaces import CONTROL_MODES, QUALIFICATION_ORDER
from .schema import Asset, Capability, Facility, MaterialLot, PropertyValue, Zone


class InventoryValidationError(ValueError):
    """The RDF is valid SBOL, but not a coherent facility catalog."""


T = TypeVar("T")


def _identity(value) -> str | None:
    return str(value) if value is not None else None


def _require_reference(document: sbol3.Document, value, expected: type[T], label: str) -> T:
    identity = _identity(value)
    if identity is None:
        raise InventoryValidationError(f"{label} is required")
    resolved = document.find(identity)
    if not isinstance(resolved, expected):
        raise InventoryValidationError(
            f"{label} refers to {identity}, which is not a {expected.__name__}"
        )
    return resolved


def _require_iri(value, label: str) -> str:
    text = str(value)
    parsed = urlparse(text)
    if (
        not parsed.scheme
        or any(character.isspace() for character in text)
        or (parsed.scheme in {"http", "https"} and not parsed.netloc)
    ):
        raise InventoryValidationError(f"{label} must be an absolute IRI, found {text!r}")
    return text


def _facility_identity(obj: Zone | Asset | MaterialLot) -> str:
    identity = _identity(obj.facility)
    if identity is None:
        raise InventoryValidationError(f"{obj.identity} does not name its facility")
    return identity


def _validate_property(value: PropertyValue, owner: str) -> None:
    if value.kind is None:
        raise InventoryValidationError(f"Property on {owner} has no kind")
    _require_iri(value.kind, f"Property kind on {owner}")
    choices = [
        value.text_value,
        value.integer_value,
        value.real_value,
        value.boolean_value,
        value.uri_value,
    ]
    count = sum(choice is not None for choice in choices)
    if count != 1:
        raise InventoryValidationError(
            f"Property {value.kind} on {owner} must have exactly one typed value"
        )
    if value.uri_value is not None:
        _require_iri(value.uri_value, f"Property {value.kind} URI value on {owner}")
    if value.unit is not None:
        _require_iri(value.unit, f"Property {value.kind} unit on {owner}")


def _validate_capability(capability: Capability, asset: Asset) -> None:
    if capability.kind is None:
        raise InventoryValidationError(f"Capability on {asset.identity} has no kind")
    _require_iri(capability.kind, f"Capability kind on {asset.identity}")
    if capability.qualification is None or str(capability.qualification) not in QUALIFICATION_ORDER:
        raise InventoryValidationError(
            f"Capability {capability.kind} on {asset.identity} has unknown qualification "
            f"{capability.qualification}"
        )
    if capability.control_mode is None or str(capability.control_mode) not in CONTROL_MODES:
        raise InventoryValidationError(
            f"Capability {capability.kind} on {asset.identity} has unknown control mode "
            f"{capability.control_mode}"
        )
    if capability.is_active is None:
        raise InventoryValidationError(
            f"Capability {capability.kind} on {asset.identity} has no lifecycle state"
        )
    for parameter in capability.parameters:
        _validate_property(parameter, str(capability.kind))


def _validate_no_cycles(
    objects: Iterable[T],
    identity: Callable[[T], str],
    parent: Callable[[T], str | None],
    label: str,
) -> None:
    by_identity = {identity(obj): obj for obj in objects}
    for start in by_identity:
        seen: set[str] = set()
        current: str | None = start
        while current is not None:
            if current in seen:
                raise InventoryValidationError(f"{label} contains a cycle through {current}")
            seen.add(current)
            obj = by_identity.get(current)
            current = parent(obj) if obj is not None else None


def _validate_asset_containment_cycles(
    document: sbol3.Document,
    assets: Iterable[Asset],
) -> None:
    """Reject cycles that mix composition and asset-to-asset location edges."""

    edges: dict[str, set[str]] = {}
    for asset in assets:
        parents = {
            identity
            for identity in (
                _identity(asset.part_of),
                _identity(asset.located_in),
            )
            if identity is not None and isinstance(document.find(identity), Asset)
        }
        edges[str(asset.identity)] = parents

    visited: set[str] = set()
    active: set[str] = set()

    def visit(identity: str) -> None:
        if identity in active:
            raise InventoryValidationError(f"Asset containment contains a cycle through {identity}")
        if identity in visited:
            return
        active.add(identity)
        for parent in edges.get(identity, ()):
            visit(parent)
        active.remove(identity)
        visited.add(identity)

    for identity in edges:
        visit(identity)


def _validate_location(
    document: sbol3.Document,
    obj: Asset | MaterialLot,
    occupied: dict[tuple[str, str], str],
) -> None:
    location_uri = _identity(obj.located_in)
    position = str(obj.position) if obj.position is not None else None
    if position is not None and not position.strip():
        raise InventoryValidationError(f"{obj.identity} has an empty position")
    if location_uri is None:
        if position is not None:
            raise InventoryValidationError(f"{obj.identity} has a position but no location")
        return
    location = document.find(location_uri)
    if not isinstance(location, (Zone, Asset)):
        raise InventoryValidationError(
            f"{obj.identity} location {location_uri} is not a Zone or Asset"
        )
    if _facility_identity(obj) != _facility_identity(location):
        raise InventoryValidationError(
            f"{obj.identity} and location {location.identity} belong to different facilities"
        )
    if isinstance(location, Zone):
        if position is not None:
            raise InventoryValidationError(
                f"{obj.identity} gives position {position} inside a zone; "
                "positions belong to assets"
            )
        return
    allowed = {str(value) for value in location.allowed_positions}
    if allowed and position is None:
        raise InventoryValidationError(
            f"{obj.identity} must name a position in container {location.identity}"
        )
    if position is not None and allowed and position not in allowed:
        raise InventoryValidationError(
            f"Position {position} is not allowed in container {location.identity}"
        )
    if position is not None:
        slot = (str(location.identity), position)
        previous = occupied.get(slot)
        if previous is not None:
            raise InventoryValidationError(
                f"Position {position} in {location.identity} is occupied by both "
                f"{previous} and {obj.identity}"
            )
        occupied[slot] = str(obj.identity)


def validate_inventory_graph(document: sbol3.Document) -> None:
    """Validate the catalog, location, capability, and material invariants."""

    facilities = [obj for obj in document.objects if isinstance(obj, Facility)]
    zones = [obj for obj in document.objects if isinstance(obj, Zone)]
    assets = [obj for obj in document.objects if isinstance(obj, Asset)]
    material_lots = [
        obj
        for obj in document.objects
        if isinstance(obj, MaterialLot) and obj.inventory_kind is not None
    ]

    facility_ids = {str(facility.identity) for facility in facilities}
    for zone in zones:
        facility = _require_reference(
            document, zone.facility, Facility, f"Zone {zone.identity} facility"
        )
        if str(facility.identity) not in facility_ids:
            raise InventoryValidationError(f"Zone {zone.identity} names an unknown facility")
        if zone.kind is None:
            raise InventoryValidationError(f"Zone {zone.identity} has no kind")
        _require_iri(zone.kind, f"Zone {zone.identity} kind")
        if zone.is_active is None:
            raise InventoryValidationError(f"Zone {zone.identity} has no lifecycle state")
        if zone.parent_zone is not None:
            parent = _require_reference(
                document, zone.parent_zone, Zone, f"Zone {zone.identity} parent"
            )
            if _facility_identity(parent) != _facility_identity(zone):
                raise InventoryValidationError(
                    f"Zone {zone.identity} and its parent belong to different facilities"
                )
        for condition in zone.conditions:
            _validate_property(condition, str(zone.identity))
        for policy in zone.policies:
            _require_iri(policy, f"Zone {zone.identity} policy")

    _validate_no_cycles(
        zones,
        lambda zone: str(zone.identity),
        lambda zone: _identity(zone.parent_zone),
        "Zone hierarchy",
    )

    for asset in assets:
        _require_reference(document, asset.facility, Facility, f"Asset {asset.identity} facility")
        if asset.kind is None:
            raise InventoryValidationError(f"Asset {asset.identity} has no kind")
        _require_iri(asset.kind, f"Asset {asset.identity} kind")
        if asset.is_active is None:
            raise InventoryValidationError(f"Asset {asset.identity} has no lifecycle state")
        positions = [str(value) for value in asset.allowed_positions]
        if any(not position.strip() for position in positions):
            raise InventoryValidationError(f"Asset {asset.identity} has an empty allowed position")
        if len(positions) != len(set(positions)):
            raise InventoryValidationError(f"Asset {asset.identity} repeats an allowed position")
        if asset.part_of is not None:
            parent = _require_reference(
                document, asset.part_of, Asset, f"Asset {asset.identity} parent"
            )
            if _facility_identity(parent) != _facility_identity(asset):
                raise InventoryValidationError(
                    f"Asset {asset.identity} and its parent belong to different facilities"
                )
        for established in asset.establishes_zones:
            zone = _require_reference(
                document, established, Zone, f"Asset {asset.identity} established zone"
            )
            if _facility_identity(zone) != _facility_identity(asset):
                raise InventoryValidationError(
                    f"Asset {asset.identity} establishes a zone in another facility"
                )
        seen_capabilities: set[str] = set()
        for capability in asset.capabilities:
            _validate_capability(capability, asset)
            kind = str(capability.kind)
            if kind in seen_capabilities:
                raise InventoryValidationError(
                    f"Asset {asset.identity} offers capability {kind} more than once; "
                    "use a child asset for a separately reservable functional unit"
                )
            seen_capabilities.add(kind)

    _validate_no_cycles(
        assets,
        lambda asset: str(asset.identity),
        lambda asset: _identity(asset.part_of),
        "Asset composition",
    )
    _validate_no_cycles(
        assets,
        lambda asset: str(asset.identity),
        lambda asset: (
            _identity(asset.located_in)
            if isinstance(document.find(_identity(asset.located_in) or ""), Asset)
            else None
        ),
        "Asset location",
    )
    _validate_asset_containment_cycles(document, assets)

    occupied: dict[tuple[str, str], str] = {}
    for asset in assets:
        _validate_location(document, asset, occupied)

    for lot in material_lots:
        _require_reference(
            document, lot.facility, Facility, f"Material lot {lot.identity} facility"
        )
        if lot.built is None:
            raise InventoryValidationError(f"Material lot {lot.identity} has no built Component")
        _require_iri(lot.inventory_kind, f"Material lot {lot.identity} kind")
        built = document.find(str(lot.built))
        if not isinstance(built, sbol3.Component):
            raise InventoryValidationError(
                f"Material lot {lot.identity} built reference does not resolve to a Component"
            )
        if lot.is_active is None:
            raise InventoryValidationError(f"Material lot {lot.identity} has no lifecycle state")
        _validate_location(document, lot, occupied)


def validate_document(document: sbol3.Document) -> None:
    """Run both the SBOL 3 validator and the facility profile validator."""

    report = document.validate()
    if report.errors:
        messages = "; ".join(str(error) for error in report.errors)
        raise InventoryValidationError(f"SBOL 3 validation failed: {messages}")
    validate_inventory_graph(document)


# Clearer name for new callers; old code can retain validate_inventory_graph.
validate_catalog = validate_inventory_graph
