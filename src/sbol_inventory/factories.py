"""Typed constructors and graph mutation helpers."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import datetime

import sbol3

from .namespaces import (
    BACTERIAL_STOCK,
    BOX,
    CONTROL_UNSPECIFIED,
    DILUTED_PLASMID,
    FRIDGE_4C,
    FRIDGE_MINUS_20,
    FRIDGE_MINUS_80,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    QUALIFICATION_DISCOVERED,
    SHELF,
    SOLID_MEDIA_PLATE,
)
from .schema import Asset, Capability, Facility, MaterialLot, PropertyValue, Reference, Zone

Scalar = str | int | float | bool


def make_facility(
    identity: str,
    *,
    name: str | None = None,
    description: str | None = None,
) -> Facility:
    return Facility(identity=identity, name=name, description=description)


def make_zone(
    identity: str,
    *,
    facility: Reference,
    kind: str,
    parent_zone: Reference | None = None,
    policies: Iterable[str] | None = None,
    conditions: Sequence[PropertyValue] | None = None,
    name: str | None = None,
    description: str | None = None,
) -> Zone:
    return Zone(
        identity=identity,
        facility=facility,
        kind=kind,
        parent_zone=parent_zone,
        policies=policies,
        conditions=conditions,
        is_active=True,
        name=name,
        description=description,
    )


def make_property(
    kind: str,
    value: Scalar,
    *,
    unit: str | None = None,
    name: str | None = None,
) -> PropertyValue:
    """Create one typed scalar property without stringifying its value."""

    kwargs: dict[str, object] = {}
    if isinstance(value, bool):
        kwargs["boolean_value"] = value
    elif isinstance(value, int):
        kwargs["integer_value"] = value
    elif isinstance(value, float):
        kwargs["real_value"] = value
    elif isinstance(value, str) and value.startswith(("http://", "https://", "urn:")):
        kwargs["uri_value"] = value
    elif isinstance(value, str):
        kwargs["text_value"] = value
    else:
        raise TypeError("Property values must be str, int, float, or bool")
    return PropertyValue(kind=kind, unit=unit, name=name, **kwargs)


def make_capability(
    kind: str,
    *,
    qualification: str = QUALIFICATION_DISCOVERED,
    control_mode: str = CONTROL_UNSPECIFIED,
    parameters: Sequence[PropertyValue] | None = None,
    name: str | None = None,
    description: str | None = None,
) -> Capability:
    return Capability(
        kind=kind,
        qualification=qualification,
        control_mode=control_mode,
        is_active=True,
        parameters=parameters,
        name=name,
        description=description,
    )


def make_asset(
    identity: str,
    *,
    facility: Reference,
    kind: str,
    located_in: Reference | None = None,
    position: str | None = None,
    part_of: Reference | None = None,
    establishes_zones: Iterable[Reference] | None = None,
    manufacturer: str | None = None,
    model: str | None = None,
    serial_number: str | None = None,
    allowed_positions: Iterable[str] | None = None,
    capabilities: Sequence[Capability] | None = None,
    name: str | None = None,
    description: str | None = None,
) -> Asset:
    return Asset(
        identity=identity,
        facility=facility,
        kind=kind,
        located_in=located_in,
        position=position,
        part_of=part_of,
        establishes_zones=establishes_zones,
        manufacturer=manufacturer,
        model=model,
        serial_number=serial_number,
        is_active=True,
        allowed_positions=allowed_positions,
        capabilities=capabilities,
        name=name,
        description=description,
    )


def make_material_lot(
    identity: str,
    *,
    built: Reference,
    facility: Reference,
    kind: str,
    located_in: Reference | None = None,
    position: str | None = None,
    barcode: str | None = None,
    lot_id: str | None = None,
    notes: str | None = None,
    freeze_date: str | datetime | None = None,
    name: str | None = None,
    description: str | None = None,
    derived_from_material: Iterable[Reference] | None = None,
    generated_by: list[str] | None = None,
    measures: list[sbol3.SBOLObject] | None = None,
) -> MaterialLot:
    return MaterialLot(
        identity=identity,
        built=built,
        inventory_kind=kind,
        facility=facility,
        located_in=located_in,
        position=position,
        is_active=True,
        barcode=barcode,
        lot_id=lot_id,
        notes=notes,
        freeze_date=freeze_date,
        name=name,
        description=description,
        derived_from_material=derived_from_material,
        generated_by=generated_by,
        measures=measures,
    )


def grid_positions(rows: Sequence[str], columns: Iterable[int]) -> list[str]:
    normalized_rows = [str(row).strip().upper() for row in rows]
    normalized_columns = [int(column) for column in columns]
    if not normalized_rows or any(len(row) != 1 or not row.isalpha() for row in normalized_rows):
        raise ValueError("Rows must be non-empty single alphabetic labels")
    if not normalized_columns or any(column < 1 for column in normalized_columns):
        raise ValueError("Columns must be positive integers")
    if len(normalized_rows) != len(set(normalized_rows)):
        raise ValueError("Container rows must be unique")
    if len(normalized_columns) != len(set(normalized_columns)):
        raise ValueError("Container columns must be unique")
    return [f"{row}{column}" for row in normalized_rows for column in normalized_columns]


def make_fridge_minus80(
    identity: str,
    *,
    facility: Reference,
    located_in: Reference | None = None,
    name: str | None = None,
) -> Asset:
    return make_asset(
        identity,
        facility=facility,
        kind=FRIDGE_MINUS_80,
        located_in=located_in,
        name=name,
    )


def make_fridge_minus20(
    identity: str,
    *,
    facility: Reference,
    located_in: Reference | None = None,
    name: str | None = None,
) -> Asset:
    return make_asset(
        identity,
        facility=facility,
        kind=FRIDGE_MINUS_20,
        located_in=located_in,
        name=name,
    )


def make_fridge_4c(
    identity: str,
    *,
    facility: Reference,
    located_in: Reference | None = None,
    name: str | None = None,
) -> Asset:
    return make_asset(
        identity,
        facility=facility,
        kind=FRIDGE_4C,
        located_in=located_in,
        name=name,
    )


def make_shelf(
    identity: str,
    *,
    facility: Reference,
    part_of: Reference,
    name: str | None = None,
    allowed_positions: Iterable[str] | None = None,
) -> Asset:
    return make_asset(
        identity,
        facility=facility,
        kind=SHELF,
        part_of=part_of,
        name=name,
        allowed_positions=allowed_positions,
    )


def make_box(
    identity: str,
    *,
    facility: Reference,
    located_in: Reference | None = None,
    position: str | None = None,
    rows: Sequence[str],
    columns: Iterable[int],
    name: str | None = None,
) -> Asset:
    return make_asset(
        identity,
        facility=facility,
        kind=BOX,
        located_in=located_in,
        position=position,
        allowed_positions=grid_positions(rows, columns),
        name=name,
    )


def make_solid_media_plate(
    identity: str,
    *,
    facility: Reference,
    located_in: Reference | None = None,
    position: str | None = None,
    rows: Sequence[str],
    columns: Iterable[int],
    name: str | None = None,
) -> Asset:
    return make_asset(
        identity,
        facility=facility,
        kind=SOLID_MEDIA_PLATE,
        located_in=located_in,
        position=position,
        allowed_positions=grid_positions(rows, columns),
        name=name,
    )


def make_solid_96_well_plate(
    identity: str,
    *,
    facility: Reference,
    located_in: Reference | None = None,
    position: str | None = None,
    name: str | None = None,
) -> Asset:
    return make_solid_media_plate(
        identity,
        facility=facility,
        located_in=located_in,
        position=position,
        rows=list("ABCDEFGH"),
        columns=range(1, 13),
        name=name,
    )


def make_single_well_petri_dish_plate(
    identity: str,
    *,
    facility: Reference,
    located_in: Reference | None = None,
    position: str | None = None,
    name: str | None = None,
) -> Asset:
    return make_solid_media_plate(
        identity,
        facility=facility,
        located_in=located_in,
        position=position,
        rows=["A"],
        columns=[1],
        name=name,
    )


def make_diluted_plasmid(
    identity: str, *, built: Reference, facility: Reference, **kwargs
) -> MaterialLot:
    return make_material_lot(
        identity, built=built, facility=facility, kind=DILUTED_PLASMID, **kwargs
    )


def make_bacterial_stock(
    identity: str, *, built: Reference, facility: Reference, **kwargs
) -> MaterialLot:
    return make_material_lot(
        identity, built=built, facility=facility, kind=BACTERIAL_STOCK, **kwargs
    )


def make_procured_material(
    identity: str, *, built: Reference, facility: Reference, **kwargs
) -> MaterialLot:
    return make_material_lot(
        identity, built=built, facility=facility, kind=PROCURED_MATERIAL, **kwargs
    )


def make_plated_strain(
    identity: str, *, built: Reference, facility: Reference, **kwargs
) -> MaterialLot:
    return make_material_lot(identity, built=built, facility=facility, kind=PLATED_STRAIN, **kwargs)


def _require_shared_document(*objects: sbol3.Identified) -> None:
    documents = [obj.document for obj in objects]
    if any(document is None for document in documents):
        raise ValueError("Add all related objects to one document before changing location")
    if any(document is not documents[0] for document in documents[1:]):
        raise ValueError("All related objects must belong to the same document")


def _facility_identity(obj: Asset | MaterialLot | Zone) -> str:
    return str(obj.facility) if obj.facility is not None else ""


def locate(
    item: Asset | MaterialLot,
    location: Zone | Asset,
    *,
    position: str | None = None,
    check_occupied: bool = True,
) -> None:
    """Locate an asset or material lot in one zone or container asset.

    ``check_occupied=False`` supports bulk graph construction, but does not
    bypass facility or coordinate checks. Final document validation still
    rejects double occupancy.
    """

    _require_shared_document(item, location)
    if str(item.identity) == str(location.identity):
        raise ValueError("An object cannot be located in itself")
    if _facility_identity(item) != _facility_identity(location):
        raise ValueError("Located objects must belong to the same facility")
    normalized_position = position.strip() if position is not None else None
    if normalized_position == "":
        raise ValueError("Position cannot be empty")
    if isinstance(location, Zone) and normalized_position is not None:
        raise ValueError("Positions belong to container assets, not zones")
    allowed = (
        {str(value) for value in location.allowed_positions}
        if isinstance(location, Asset)
        else set()
    )
    if allowed and normalized_position is None:
        raise ValueError(f"Location {location.identity} requires a position")
    if normalized_position is not None and allowed and normalized_position not in allowed:
        raise ValueError(f"Position {normalized_position} is not allowed in {location.identity}")
    if normalized_position is not None and check_occupied:
        for other in location.document.objects:
            if other is item or not isinstance(other, (Asset, MaterialLot)):
                continue
            if (
                other.located_in is not None
                and str(other.located_in) == str(location.identity)
                and other.position is not None
                and str(other.position) == normalized_position
            ):
                raise ValueError(
                    f"Position {normalized_position} in {location.identity} is occupied by "
                    f"{other.identity}"
                )
    item.located_in = location.identity
    item.position = normalized_position


def place_in_container(
    container: Asset,
    item: Asset | MaterialLot,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    position = f"{str(row).strip().upper()}{int(column)}"
    locate(item, container, position=position, check_occupied=check_occupied)


def place_in_plate(
    plate: Asset,
    item: Asset | MaterialLot,
    well: str,
    *,
    check_occupied: bool = True,
) -> None:
    normalized = str(well).strip().upper()
    if len(normalized) < 2 or not normalized[0].isalpha() or not normalized[1:].isdigit():
        raise ValueError(f"Invalid well position '{well}'. Expected format like 'A1'.")
    place_in_container(
        plate,
        item,
        row=normalized[0],
        column=int(normalized[1:]),
        check_occupied=check_occupied,
    )


def move_item(
    item: Asset | MaterialLot,
    new_container: Asset,
    row: str,
    column: int,
    *,
    check_occupied: bool = True,
) -> None:
    place_in_container(
        new_container,
        item,
        row,
        column,
        check_occupied=check_occupied,
    )


def remove_from_container(item: Asset | MaterialLot) -> None:
    item.located_in = None
    item.position = None


def discard(item: Asset | MaterialLot) -> None:
    item.is_active = False


# Compatibility names whose semantics remain honest in the new model.
make_square_96_position_plate = make_solid_96_well_plate
discard_implementation = discard
place_item = locate


def add_child(parent: Zone | Asset, child: Asset | MaterialLot) -> None:
    """Compatibility helper for direct location without a container position."""

    locate(child, parent)
