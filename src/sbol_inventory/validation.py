"""Semantic validation beyond the SBOL 3 core rules."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable
from typing import TypeVar
from urllib.parse import urlparse

import sbol3

from .namespaces import CONTROL_MODES, QUALIFICATION_ORDER, RUN_ASSET, RUN_INPUT_MATERIAL
from .rules import (
    ASSET_ACTIVE_RULE,
    ASSET_ALLOWED_POSITION_RULE,
    ASSET_CAPABILITY_KIND_RULE,
    ASSET_CONTAINMENT_CYCLE_RULE,
    ASSET_ESTABLISHES_ZONE_RULE,
    ASSET_FACILITY_RULE,
    ASSET_KIND_RULE,
    ASSET_PART_OF_RULE,
    CAPABILITY_ACTIVE_RULE,
    CAPABILITY_CONTROL_MODE_RULE,
    CAPABILITY_KIND_RULE,
    CAPABILITY_OWNER_RULE,
    CAPABILITY_PARAMETER_KIND_RULE,
    CAPABILITY_QUALIFICATION_RULE,
    LOCATION_FACILITY_RULE,
    LOCATION_OCCUPANCY_RULE,
    LOCATION_POSITION_RULE,
    MATERIAL_ACTIVE_RULE,
    MATERIAL_BUILT_RULE,
    MATERIAL_FACILITY_RULE,
    MATERIAL_KIND_RULE,
    MATERIAL_LINEAGE_RULE,
    PROPERTY_IRI_RULE,
    PROPERTY_KIND_RULE,
    PROPERTY_OWNER_RULE,
    PROPERTY_UNIT_RULE,
    PROPERTY_VALUE_RULE,
    RUN_ASSET_RULE,
    RUN_INPUT_MATERIAL_RULE,
    RUN_REQUIRES_ASSET_RULE,
    SBOL_CORE_RULE,
    ZONE_ACTIVE_RULE,
    ZONE_CONDITION_KIND_RULE,
    ZONE_CYCLE_RULE,
    ZONE_FACILITY_RULE,
    ZONE_KIND_RULE,
    ZONE_PARENT_RULE,
    ZONE_POLICY_RULE,
)
from .schema import Asset, Capability, Facility, MaterialLot, PropertyValue, Zone


class InventoryValidationError(ValueError):
    """A stable SBOLInventory rule violation."""

    def __init__(self, rule_id: str, message: str):
        self.rule_id = rule_id
        self.message = message
        super().__init__(f"[{rule_id}] {message}")


T = TypeVar("T")


def _identity(value) -> str | None:
    return str(value) if value is not None else None


def _require_reference(
    document: sbol3.Document,
    value,
    expected: type[T],
    label: str,
    rule_id: str,
) -> T:
    identity = _identity(value)
    if identity is None:
        raise InventoryValidationError(rule_id, f"{label} is required")
    resolved = document.find(identity)
    if not isinstance(resolved, expected):
        raise InventoryValidationError(
            rule_id,
            f"{label} refers to {identity}, which is not a document-local {expected.__name__}",
        )
    return resolved


def _require_iri(value, label: str, rule_id: str) -> str:
    text = str(value)
    parsed = urlparse(text)
    if (
        not parsed.scheme
        or any(character.isspace() for character in text)
        or (parsed.scheme in {"http", "https"} and not parsed.netloc)
    ):
        raise InventoryValidationError(
            rule_id,
            f"{label} must be an absolute IRI, found {text!r}",
        )
    return text


def _facility_identity(obj: Zone | Asset | MaterialLot, rule_id: str) -> str:
    identity = _identity(obj.facility)
    if identity is None:
        raise InventoryValidationError(rule_id, f"{obj.identity} does not name its facility")
    return identity


def _validate_property(value: PropertyValue, owner: str) -> None:
    if value.kind is None:
        raise InventoryValidationError(PROPERTY_KIND_RULE, f"Property on {owner} has no kind")
    _require_iri(value.kind, f"Property kind on {owner}", PROPERTY_KIND_RULE)
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
            PROPERTY_VALUE_RULE,
            f"Property {value.kind} on {owner} must have exactly one typed value",
        )
    if value.uri_value is not None:
        _require_iri(
            value.uri_value,
            f"Property {value.kind} URI value on {owner}",
            PROPERTY_IRI_RULE,
        )
    if value.unit is not None:
        _require_iri(value.unit, f"Property {value.kind} unit on {owner}", PROPERTY_IRI_RULE)
        if value.integer_value is None and value.real_value is None:
            raise InventoryValidationError(
                PROPERTY_UNIT_RULE,
                f"Property {value.kind} on {owner} has a unit but no numeric value",
            )


def _validate_unique_property_kinds(
    values: Iterable[PropertyValue],
    owner: str,
    rule_id: str,
) -> None:
    kinds = [str(value.kind) for value in values if value.kind is not None]
    duplicates = sorted(kind for kind, count in Counter(kinds).items() if count > 1)
    if duplicates:
        raise InventoryValidationError(
            rule_id,
            f"{owner} repeats property kind {duplicates[0]}",
        )


def _validate_capability(capability: Capability, asset: Asset) -> None:
    if capability.kind is None:
        raise InventoryValidationError(
            CAPABILITY_KIND_RULE,
            f"Capability on {asset.identity} has no kind",
        )
    _require_iri(
        capability.kind,
        f"Capability kind on {asset.identity}",
        CAPABILITY_KIND_RULE,
    )
    if capability.qualification is None or str(capability.qualification) not in QUALIFICATION_ORDER:
        raise InventoryValidationError(
            CAPABILITY_QUALIFICATION_RULE,
            f"Capability {capability.kind} on {asset.identity} has unknown qualification "
            f"{capability.qualification}",
        )
    if capability.control_mode is None or str(capability.control_mode) not in CONTROL_MODES:
        raise InventoryValidationError(
            CAPABILITY_CONTROL_MODE_RULE,
            f"Capability {capability.kind} on {asset.identity} has unknown control mode "
            f"{capability.control_mode}",
        )
    if capability.is_active is None:
        raise InventoryValidationError(
            CAPABILITY_ACTIVE_RULE,
            f"Capability {capability.kind} on {asset.identity} has no lifecycle state",
        )
    for parameter in capability.parameters:
        _validate_property(parameter, str(capability.kind))
    _validate_unique_property_kinds(
        capability.parameters,
        f"Capability {capability.kind} on {asset.identity}",
        CAPABILITY_PARAMETER_KIND_RULE,
    )


def _validate_no_cycles(
    objects: Iterable[T],
    identity: Callable[[T], str],
    parent: Callable[[T], str | None],
    label: str,
    rule_id: str,
) -> None:
    by_identity = {identity(obj): obj for obj in objects}
    for start in by_identity:
        seen: set[str] = set()
        current: str | None = start
        while current is not None:
            if current in seen:
                raise InventoryValidationError(
                    rule_id,
                    f"{label} contains a cycle through {current}",
                )
            seen.add(current)
            obj = by_identity.get(current)
            current = parent(obj) if obj is not None else None


def _validate_asset_containment_cycles(
    document: sbol3.Document,
    assets: Iterable[Asset],
) -> None:
    edges: dict[str, set[str]] = {}
    for asset in assets:
        parents = {
            identity
            for identity in (_identity(asset.part_of), _identity(asset.located_in))
            if identity is not None and isinstance(document.find(identity), Asset)
        }
        edges[str(asset.identity)] = parents

    visited: set[str] = set()
    active: set[str] = set()

    def visit(identity: str) -> None:
        if identity in active:
            raise InventoryValidationError(
                ASSET_CONTAINMENT_CYCLE_RULE,
                f"Asset containment contains a cycle through {identity}",
            )
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
        raise InventoryValidationError(
            LOCATION_POSITION_RULE,
            f"{obj.identity} has an empty position",
        )
    if location_uri is None:
        if position is not None:
            raise InventoryValidationError(
                LOCATION_POSITION_RULE,
                f"{obj.identity} has a position but no location",
            )
        return
    location = document.find(location_uri)
    if not isinstance(location, (Zone, Asset)):
        raise InventoryValidationError(
            LOCATION_FACILITY_RULE,
            f"{obj.identity} location {location_uri} is not a document-local Zone or Asset",
        )
    if _facility_identity(obj, LOCATION_FACILITY_RULE) != _facility_identity(
        location, LOCATION_FACILITY_RULE
    ):
        raise InventoryValidationError(
            LOCATION_FACILITY_RULE,
            f"{obj.identity} and location {location.identity} belong to different facilities",
        )
    if isinstance(location, Zone):
        if position is not None:
            raise InventoryValidationError(
                LOCATION_POSITION_RULE,
                f"{obj.identity} gives position {position} inside a zone; "
                "positions belong to assets",
            )
        return
    allowed = {str(value) for value in location.allowed_positions}
    if allowed and position is None:
        raise InventoryValidationError(
            LOCATION_POSITION_RULE,
            f"{obj.identity} must name a position in container {location.identity}",
        )
    if position is not None and allowed and position not in allowed:
        raise InventoryValidationError(
            LOCATION_POSITION_RULE,
            f"Position {position} is not allowed in container {location.identity}",
        )
    if position is not None:
        slot = (str(location.identity), position)
        previous = occupied.get(slot)
        if previous is not None:
            raise InventoryValidationError(
                LOCATION_OCCUPANCY_RULE,
                f"Position {position} in {location.identity} is occupied by both "
                f"{previous} and {obj.identity}",
            )
        occupied[slot] = str(obj.identity)


def _validate_owned_object_uniqueness(zones: Iterable[Zone], assets: Iterable[Asset]) -> None:
    capability_owners: Counter[str] = Counter()
    property_owners: Counter[str] = Counter()
    for zone in zones:
        property_owners.update(str(condition.identity) for condition in zone.conditions)
    for asset in assets:
        capability_owners.update(str(capability.identity) for capability in asset.capabilities)
        for capability in asset.capabilities:
            property_owners.update(str(parameter.identity) for parameter in capability.parameters)
    repeated_capabilities = sorted(
        identity for identity, count in capability_owners.items() if count != 1
    )
    if repeated_capabilities:
        raise InventoryValidationError(
            CAPABILITY_OWNER_RULE,
            f"CapabilityOffering {repeated_capabilities[0]} is owned by more than one Asset",
        )
    repeated_properties = sorted(
        identity for identity, count in property_owners.items() if count != 1
    )
    if repeated_properties:
        raise InventoryValidationError(
            PROPERTY_OWNER_RULE,
            f"PropertyValue {repeated_properties[0]} is owned more than once",
        )


def _validate_material_lineage(
    document: sbol3.Document,
    material_lots: Iterable[MaterialLot],
) -> None:
    lots = {str(lot.identity): lot for lot in material_lots}
    edges: dict[str, set[str]] = {}
    for lot in lots.values():
        identity = str(lot.identity)
        derived_from_material: set[str] = set()
        for reference in lot.derived_from_material:
            source_identity = str(reference)
            source = document.find(source_identity)
            if not isinstance(source, MaterialLot) or source.inventory_kind is None:
                raise InventoryValidationError(
                    MATERIAL_LINEAGE_RULE,
                    f"Material lot {identity} derives from {source_identity}, which is not a "
                    "document-local MaterialLot",
                )
            if source_identity == identity:
                raise InventoryValidationError(
                    MATERIAL_LINEAGE_RULE,
                    f"Material lot {identity} derives from itself",
                )
            derived_from_material.add(source_identity)
        edges[identity] = derived_from_material

    visited: set[str] = set()
    active: set[str] = set()

    def visit(identity: str) -> None:
        if identity in active:
            raise InventoryValidationError(
                MATERIAL_LINEAGE_RULE,
                f"Material lineage contains a cycle through {identity}",
            )
        if identity in visited:
            return
        active.add(identity)
        for source in edges.get(identity, ()):
            visit(source)
        active.remove(identity)
        visited.add(identity)

    for identity in edges:
        visit(identity)


def _validate_profile_runs(document: sbol3.Document) -> None:
    for obj in document.objects:
        if not isinstance(obj, sbol3.Activity):
            continue
        profile_usage_count = 0
        run_asset_count = 0
        for usage in obj.usage:
            roles = {str(role) for role in usage.roles}
            if RUN_ASSET in roles:
                profile_usage_count += 1
                run_asset_count += 1
                _require_reference(
                    document,
                    usage.entity,
                    Asset,
                    f"Run {obj.identity} asset usage entity",
                    RUN_ASSET_RULE,
                )
            if RUN_INPUT_MATERIAL in roles:
                profile_usage_count += 1
                material = _require_reference(
                    document,
                    usage.entity,
                    MaterialLot,
                    f"Run {obj.identity} input-material usage entity",
                    RUN_INPUT_MATERIAL_RULE,
                )
                if material.inventory_kind is None:
                    raise InventoryValidationError(
                        RUN_INPUT_MATERIAL_RULE,
                        f"Run {obj.identity} input usage does not refer to a MaterialLot",
                    )
        if profile_usage_count and not run_asset_count:
            raise InventoryValidationError(
                RUN_REQUIRES_ASSET_RULE,
                f"Profile run {obj.identity} has no RunAsset usage",
            )


def validate_inventory_graph(document: sbol3.Document) -> None:
    """Validate the catalog, location, capability, material, and run invariants."""

    zones = [obj for obj in document.objects if isinstance(obj, Zone)]
    assets = [obj for obj in document.objects if isinstance(obj, Asset)]
    material_lots = [
        obj
        for obj in document.objects
        if isinstance(obj, MaterialLot) and obj.inventory_kind is not None
    ]

    _validate_owned_object_uniqueness(zones, assets)

    for zone in zones:
        _require_reference(
            document,
            zone.facility,
            Facility,
            f"Zone {zone.identity} facility",
            ZONE_FACILITY_RULE,
        )
        if zone.kind is None:
            raise InventoryValidationError(ZONE_KIND_RULE, f"Zone {zone.identity} has no kind")
        _require_iri(zone.kind, f"Zone {zone.identity} kind", ZONE_KIND_RULE)
        if zone.is_active is None:
            raise InventoryValidationError(
                ZONE_ACTIVE_RULE,
                f"Zone {zone.identity} has no lifecycle state",
            )
        if zone.parent_zone is not None:
            parent = _require_reference(
                document,
                zone.parent_zone,
                Zone,
                f"Zone {zone.identity} parent",
                ZONE_PARENT_RULE,
            )
            if _facility_identity(parent, ZONE_PARENT_RULE) != _facility_identity(
                zone, ZONE_PARENT_RULE
            ):
                raise InventoryValidationError(
                    ZONE_PARENT_RULE,
                    f"Zone {zone.identity} and its parent belong to different facilities",
                )
        for condition in zone.conditions:
            _validate_property(condition, str(zone.identity))
        _validate_unique_property_kinds(
            zone.conditions,
            f"Zone {zone.identity}",
            ZONE_CONDITION_KIND_RULE,
        )
        for policy in zone.policies:
            _require_iri(policy, f"Zone {zone.identity} policy", ZONE_POLICY_RULE)

    _validate_no_cycles(
        zones,
        lambda zone: str(zone.identity),
        lambda zone: _identity(zone.parent_zone),
        "Zone hierarchy",
        ZONE_CYCLE_RULE,
    )

    for asset in assets:
        _require_reference(
            document,
            asset.facility,
            Facility,
            f"Asset {asset.identity} facility",
            ASSET_FACILITY_RULE,
        )
        if asset.kind is None:
            raise InventoryValidationError(ASSET_KIND_RULE, f"Asset {asset.identity} has no kind")
        _require_iri(asset.kind, f"Asset {asset.identity} kind", ASSET_KIND_RULE)
        if asset.is_active is None:
            raise InventoryValidationError(
                ASSET_ACTIVE_RULE,
                f"Asset {asset.identity} has no lifecycle state",
            )
        positions = [str(value) for value in asset.allowed_positions]
        if any(not position.strip() for position in positions):
            raise InventoryValidationError(
                ASSET_ALLOWED_POSITION_RULE,
                f"Asset {asset.identity} has an empty allowed position",
            )
        if len(positions) != len(set(positions)):
            raise InventoryValidationError(
                ASSET_ALLOWED_POSITION_RULE,
                f"Asset {asset.identity} repeats an allowed position",
            )
        if asset.part_of is not None:
            parent = _require_reference(
                document,
                asset.part_of,
                Asset,
                f"Asset {asset.identity} parent",
                ASSET_PART_OF_RULE,
            )
            if _facility_identity(parent, ASSET_PART_OF_RULE) != _facility_identity(
                asset, ASSET_PART_OF_RULE
            ):
                raise InventoryValidationError(
                    ASSET_PART_OF_RULE,
                    f"Asset {asset.identity} and its parent belong to different facilities",
                )
        for established in asset.establishes_zones:
            zone = _require_reference(
                document,
                established,
                Zone,
                f"Asset {asset.identity} established zone",
                ASSET_ESTABLISHES_ZONE_RULE,
            )
            if _facility_identity(zone, ASSET_ESTABLISHES_ZONE_RULE) != _facility_identity(
                asset, ASSET_ESTABLISHES_ZONE_RULE
            ):
                raise InventoryValidationError(
                    ASSET_ESTABLISHES_ZONE_RULE,
                    f"Asset {asset.identity} establishes a zone in another facility",
                )
        seen_capabilities: set[str] = set()
        for capability in asset.capabilities:
            _validate_capability(capability, asset)
            kind = str(capability.kind)
            if kind in seen_capabilities:
                raise InventoryValidationError(
                    ASSET_CAPABILITY_KIND_RULE,
                    f"Asset {asset.identity} offers capability {kind} more than once; use a child "
                    "asset for a separately bindable functional unit",
                )
            seen_capabilities.add(kind)

    _validate_asset_containment_cycles(document, assets)

    occupied: dict[tuple[str, str], str] = {}
    for asset in assets:
        _validate_location(document, asset, occupied)

    for lot in material_lots:
        _require_iri(lot.inventory_kind, f"Material lot {lot.identity} kind", MATERIAL_KIND_RULE)
        _require_reference(
            document,
            lot.facility,
            Facility,
            f"Material lot {lot.identity} facility",
            MATERIAL_FACILITY_RULE,
        )
        if lot.built is None:
            raise InventoryValidationError(
                MATERIAL_BUILT_RULE,
                f"Material lot {lot.identity} has no built Component",
            )
        _require_reference(
            document,
            lot.built,
            sbol3.Component,
            f"Material lot {lot.identity} built reference",
            MATERIAL_BUILT_RULE,
        )
        if lot.is_active is None:
            raise InventoryValidationError(
                MATERIAL_ACTIVE_RULE,
                f"Material lot {lot.identity} has no lifecycle state",
            )
        _validate_location(document, lot, occupied)

    _validate_material_lineage(document, material_lots)
    _validate_profile_runs(document)


def validate_document(document: sbol3.Document) -> None:
    """Run the facility-profile validator and the pySBOL3 core validator."""

    validate_inventory_graph(document)
    report = document.validate()
    if report.errors:
        messages = "; ".join(str(error) for error in report.errors)
        raise InventoryValidationError(
            SBOL_CORE_RULE,
            f"SBOL 3 validation failed: {messages}",
        )


validate_catalog = validate_inventory_graph
