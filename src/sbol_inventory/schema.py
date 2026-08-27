"""pySBOL3 classes for facility catalogs and physical material lots."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from datetime import datetime

import sbol3

from .namespaces import (
    ASSET,
    CAPABILITY_OFFERING,
    CONTROL_UNSPECIFIED,
    FACILITY,
    FACILITY_NS,
    PROPERTY_VALUE,
    QUALIFICATION_DISCOVERED,
    ZONE,
)

Reference = str | sbol3.Identified


class PropertyValue(sbol3.CustomIdentified):
    """One typed capability parameter or environmental condition."""

    TYPE_URI = PROPERTY_VALUE
    KIND_URI = FACILITY_NS + "propertyKind"
    TEXT_VALUE_URI = FACILITY_NS + "textValue"
    INTEGER_VALUE_URI = FACILITY_NS + "integerValue"
    REAL_VALUE_URI = FACILITY_NS + "realValue"
    BOOLEAN_VALUE_URI = FACILITY_NS + "booleanValue"
    URI_VALUE_URI = FACILITY_NS + "uriValue"
    UNIT_URI = FACILITY_NS + "unit"

    def __init__(
        self,
        identity: str | None = None,
        *,
        kind: str | None = None,
        text_value: str | None = None,
        integer_value: int | None = None,
        real_value: float | None = None,
        boolean_value: bool | None = None,
        uri_value: str | None = None,
        unit: str | None = None,
        name: str | None = None,
        type_uri: str = TYPE_URI,
    ):
        super().__init__(identity=identity, type_uri=type_uri, name=name)
        self.kind = sbol3.URIProperty(self, self.KIND_URI, 0, 1, initial_value=kind)
        self.text_value = sbol3.TextProperty(
            self, self.TEXT_VALUE_URI, 0, 1, initial_value=text_value
        )
        self.integer_value = sbol3.IntProperty(
            self, self.INTEGER_VALUE_URI, 0, 1, initial_value=integer_value
        )
        self.real_value = sbol3.FloatProperty(
            self, self.REAL_VALUE_URI, 0, 1, initial_value=real_value
        )
        self.boolean_value = sbol3.BooleanProperty(
            self, self.BOOLEAN_VALUE_URI, 0, 1, initial_value=boolean_value
        )
        self.uri_value = sbol3.URIProperty(self, self.URI_VALUE_URI, 0, 1, initial_value=uri_value)
        self.unit = sbol3.URIProperty(self, self.UNIT_URI, 0, 1, initial_value=unit)


class Capability(sbol3.CustomIdentified):
    """A capability offered by one installed asset at one facility."""

    TYPE_URI = CAPABILITY_OFFERING
    KIND_URI = FACILITY_NS + "capabilityKind"
    QUALIFICATION_URI = FACILITY_NS + "qualification"
    CONTROL_MODE_URI = FACILITY_NS + "controlMode"
    CAPACITY_GROUP_URI = FACILITY_NS + "capacityGroup"
    ACTIVE_URI = FACILITY_NS + "isActive"
    PARAMETER_URI = FACILITY_NS + "parameter"

    def __init__(
        self,
        identity: str | None = None,
        *,
        kind: str | None = None,
        qualification: str | None = QUALIFICATION_DISCOVERED,
        control_mode: str | None = CONTROL_UNSPECIFIED,
        capacity_group: str | None = None,
        is_active: bool | None = True,
        parameters: Sequence[PropertyValue] | None = None,
        name: str | None = None,
        description: str | None = None,
        type_uri: str = TYPE_URI,
    ):
        super().__init__(
            identity=identity,
            type_uri=type_uri,
            name=name,
            description=description,
        )
        self.kind = sbol3.URIProperty(self, self.KIND_URI, 0, 1, initial_value=kind)
        self.qualification = sbol3.URIProperty(
            self, self.QUALIFICATION_URI, 0, 1, initial_value=qualification
        )
        self.control_mode = sbol3.URIProperty(
            self, self.CONTROL_MODE_URI, 0, 1, initial_value=control_mode
        )
        self.capacity_group = sbol3.TextProperty(
            self, self.CAPACITY_GROUP_URI, 0, 1, initial_value=capacity_group
        )
        self.is_active = sbol3.BooleanProperty(self, self.ACTIVE_URI, 0, 1, initial_value=is_active)
        self.parameters = sbol3.OwnedObject(
            self,
            self.PARAMETER_URI,
            0,
            math.inf,
            initial_value=parameters,
            type_constraint=PropertyValue,
        )


class Facility(sbol3.CustomTopLevel):
    """A laboratory site whose zones, assets, and material lots share an identity scope."""

    TYPE_URI = FACILITY

    def __init__(
        self,
        identity: str | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        type_uri: str = TYPE_URI,
    ):
        super().__init__(
            identity=identity,
            type_uri=type_uri,
            name=name,
            description=description,
        )


class Zone(sbol3.CustomTopLevel):
    """A spatial, environmental, storage, or policy boundary in a facility."""

    TYPE_URI = ZONE
    FACILITY_URI = FACILITY_NS + "facility"
    PARENT_ZONE_URI = FACILITY_NS + "parentZone"
    KIND_URI = FACILITY_NS + "zoneKind"
    POLICY_URI = FACILITY_NS + "policy"
    CONDITION_URI = FACILITY_NS + "condition"
    ACTIVE_URI = FACILITY_NS + "isActive"

    def __init__(
        self,
        identity: str | None = None,
        *,
        facility: Reference | None = None,
        kind: str | None = None,
        parent_zone: Reference | None = None,
        policies: Iterable[str] | None = None,
        conditions: Sequence[PropertyValue] | None = None,
        is_active: bool | None = True,
        name: str | None = None,
        description: str | None = None,
        type_uri: str = TYPE_URI,
    ):
        super().__init__(
            identity=identity,
            type_uri=type_uri,
            name=name,
            description=description,
        )
        self.facility = sbol3.ReferencedObject(
            self, self.FACILITY_URI, 0, 1, initial_value=facility
        )
        self.kind = sbol3.URIProperty(self, self.KIND_URI, 0, 1, initial_value=kind)
        self.parent_zone = sbol3.ReferencedObject(
            self, self.PARENT_ZONE_URI, 0, 1, initial_value=parent_zone
        )
        self.policies = sbol3.URIProperty(
            self, self.POLICY_URI, 0, math.inf, initial_value=policies
        )
        self.conditions = sbol3.OwnedObject(
            self,
            self.CONDITION_URI,
            0,
            math.inf,
            initial_value=conditions,
            type_constraint=PropertyValue,
        )
        self.is_active = sbol3.BooleanProperty(self, self.ACTIVE_URI, 0, 1, initial_value=is_active)


class Asset(sbol3.CustomTopLevel):
    """A physical resource, container, instrument, or functional unit."""

    TYPE_URI = ASSET
    FACILITY_URI = FACILITY_NS + "facility"
    KIND_URI = FACILITY_NS + "assetKind"
    LOCATED_IN_URI = FACILITY_NS + "locatedIn"
    POSITION_URI = FACILITY_NS + "position"
    PART_OF_URI = FACILITY_NS + "partOf"
    ESTABLISHES_ZONE_URI = FACILITY_NS + "establishesZone"
    MANUFACTURER_URI = FACILITY_NS + "manufacturer"
    MODEL_URI = FACILITY_NS + "model"
    SERIAL_NUMBER_URI = FACILITY_NS + "serialNumber"
    ACTIVE_URI = FACILITY_NS + "isActive"
    ALLOWED_POSITION_URI = FACILITY_NS + "allowedPosition"
    CAPABILITY_URI = FACILITY_NS + "capability"

    def __init__(
        self,
        identity: str | None = None,
        *,
        facility: Reference | None = None,
        kind: str | None = None,
        located_in: Reference | None = None,
        position: str | None = None,
        part_of: Reference | None = None,
        establishes_zones: Iterable[Reference] | None = None,
        manufacturer: str | None = None,
        model: str | None = None,
        serial_number: str | None = None,
        is_active: bool | None = True,
        allowed_positions: Iterable[str] | None = None,
        capabilities: Sequence[Capability] | None = None,
        name: str | None = None,
        description: str | None = None,
        type_uri: str = TYPE_URI,
    ):
        super().__init__(
            identity=identity,
            type_uri=type_uri,
            name=name,
            description=description,
        )
        self.facility = sbol3.ReferencedObject(
            self, self.FACILITY_URI, 0, 1, initial_value=facility
        )
        self.kind = sbol3.URIProperty(self, self.KIND_URI, 0, 1, initial_value=kind)
        self.located_in = sbol3.ReferencedObject(
            self, self.LOCATED_IN_URI, 0, 1, initial_value=located_in
        )
        self.position = sbol3.TextProperty(self, self.POSITION_URI, 0, 1, initial_value=position)
        self.part_of = sbol3.ReferencedObject(self, self.PART_OF_URI, 0, 1, initial_value=part_of)
        self.establishes_zones = sbol3.ReferencedObject(
            self,
            self.ESTABLISHES_ZONE_URI,
            0,
            math.inf,
            initial_value=establishes_zones,
        )
        self.manufacturer = sbol3.TextProperty(
            self, self.MANUFACTURER_URI, 0, 1, initial_value=manufacturer
        )
        self.model = sbol3.TextProperty(self, self.MODEL_URI, 0, 1, initial_value=model)
        self.serial_number = sbol3.TextProperty(
            self, self.SERIAL_NUMBER_URI, 0, 1, initial_value=serial_number
        )
        self.is_active = sbol3.BooleanProperty(self, self.ACTIVE_URI, 0, 1, initial_value=is_active)
        self.allowed_positions = sbol3.TextProperty(
            self,
            self.ALLOWED_POSITION_URI,
            0,
            math.inf,
            initial_value=allowed_positions,
        )
        self.capabilities = sbol3.OwnedObject(
            self,
            self.CAPABILITY_URI,
            0,
            math.inf,
            initial_value=capabilities,
            type_constraint=Capability,
        )


class MaterialLot(sbol3.Implementation):
    """A physical sample or reagent lot represented by SBOL Implementation."""

    INVENTORY_KIND_URI = FACILITY_NS + "materialKind"
    FACILITY_URI = FACILITY_NS + "facility"
    LOCATED_IN_URI = FACILITY_NS + "locatedIn"
    POSITION_URI = FACILITY_NS + "position"
    ACTIVE_URI = FACILITY_NS + "isActive"
    BARCODE_URI = FACILITY_NS + "barcode"
    LOT_ID_URI = FACILITY_NS + "lotId"
    NOTES_URI = FACILITY_NS + "notes"
    FREEZE_DATE_URI = FACILITY_NS + "freezeDate"

    def __init__(
        self,
        identity: str,
        built: Reference | None = None,
        *,
        inventory_kind: str | None = None,
        facility: Reference | None = None,
        located_in: Reference | None = None,
        position: str | None = None,
        is_active: bool | None = True,
        barcode: str | None = None,
        lot_id: str | None = None,
        notes: str | None = None,
        freeze_date: str | datetime | None = None,
        namespace: str | None = None,
        name: str | None = None,
        description: str | None = None,
        derived_from: list[str] | None = None,
        generated_by: list[str] | None = None,
        measures: list[sbol3.SBOLObject] | None = None,
        type_uri: str = sbol3.SBOL_IMPLEMENTATION,
    ):
        super().__init__(
            identity=identity,
            built=built,
            namespace=namespace,
            name=name,
            description=description,
            derived_from=derived_from,
            generated_by=generated_by,
            measures=measures,
            type_uri=type_uri,
        )
        self.inventory_kind = sbol3.URIProperty(
            self, self.INVENTORY_KIND_URI, 0, 1, initial_value=inventory_kind
        )
        self.facility = sbol3.ReferencedObject(
            self, self.FACILITY_URI, 0, 1, initial_value=facility
        )
        self.located_in = sbol3.ReferencedObject(
            self, self.LOCATED_IN_URI, 0, 1, initial_value=located_in
        )
        self.position = sbol3.TextProperty(self, self.POSITION_URI, 0, 1, initial_value=position)
        self.is_active = sbol3.BooleanProperty(self, self.ACTIVE_URI, 0, 1, initial_value=is_active)
        self.barcode = sbol3.TextProperty(self, self.BARCODE_URI, 0, 1, initial_value=barcode)
        self.lot_id = sbol3.TextProperty(self, self.LOT_ID_URI, 0, 1, initial_value=lot_id)
        self.notes = sbol3.TextProperty(self, self.NOTES_URI, 0, 1, initial_value=notes)
        self.freeze_date = sbol3.DateTimeProperty(
            self, self.FREEZE_DATE_URI, 0, 1, initial_value=freeze_date
        )


def _build_facility(*, identity: str, type_uri: str) -> Facility:
    return Facility(identity=identity, type_uri=type_uri)


def _build_zone(*, identity: str, type_uri: str) -> Zone:
    return Zone(identity=identity, is_active=None, type_uri=type_uri)


def _build_asset(*, identity: str, type_uri: str) -> Asset:
    return Asset(identity=identity, is_active=None, type_uri=type_uri)


def _build_capability(*, identity: str, type_uri: str) -> Capability:
    return Capability(
        identity=identity,
        qualification=None,
        control_mode=None,
        is_active=None,
        type_uri=type_uri,
    )


def _build_property_value(*, identity: str, type_uri: str) -> PropertyValue:
    return PropertyValue(identity=identity, type_uri=type_uri)


def _build_material_lot(*, identity: str, type_uri: str) -> MaterialLot:
    return MaterialLot(identity=identity, is_active=None, type_uri=type_uri)


_REGISTERED = False


def register_extensions() -> None:
    """Register profile builders used when pySBOL3 parses RDF.

    The standard Implementation builder is intentionally decorated with the
    optional material-custody properties. Generic Implementations remain valid
    and are ignored by inventory validation unless ``materialKind`` is present.
    """

    global _REGISTERED
    if _REGISTERED:
        return
    sbol3.Document.register_builder(Facility.TYPE_URI, _build_facility)
    sbol3.Document.register_builder(Zone.TYPE_URI, _build_zone)
    sbol3.Document.register_builder(Asset.TYPE_URI, _build_asset)
    sbol3.Document.register_builder(Capability.TYPE_URI, _build_capability)
    sbol3.Document.register_builder(PropertyValue.TYPE_URI, _build_property_value)
    sbol3.Document.register_builder(sbol3.SBOL_IMPLEMENTATION, _build_material_lot)
    _REGISTERED = True


register_extensions()
