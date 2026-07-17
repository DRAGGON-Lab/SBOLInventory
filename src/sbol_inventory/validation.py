"""Validation helpers for SBOLInventory."""

from __future__ import annotations

import re
from typing import Iterable, Sequence

from .namespaces import (
    DILUTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    BOX,
    FRIDGE_MINUS_80,
    FRIDGE_MINUS_20,
    FRIDGE_4C,
    SHELF,
)
from .schema import InventoryImplementation, StorageCollection


KNOWN_KINDS = {
    DILUTED_PLASMID,
    BACTERIAL_STOCK,
    SOLID_MEDIA_PLATE,
    PLATED_STRAIN,
    PROCURED_MATERIAL,
    BOX,
}
CONTAINER_KINDS = {SOLID_MEDIA_PLATE, BOX}
STORAGE_KINDS = {FRIDGE_MINUS_80, FRIDGE_MINUS_20, FRIDGE_4C, SHELF}
WELL_96_RE = re.compile(r"^[A-H](?:[1-9]|1[0-2])$")


def validate_item(item: InventoryImplementation) -> None:
    """Validate an inventory object at the item level."""
    kind = str(item.inventory_kind)

    if kind not in KNOWN_KINDS:
        raise ValueError(f"Unknown inventory kind: {kind}")

    if not item.built:
        raise ValueError(f"{item.identity} is missing a built reference")


def validate_placement(item: InventoryImplementation, storage: StorageCollection) -> None:
    """Validate whether an item is allowed to be placed in a storage collection."""
    allowed = set(storage.allowed_item_kinds)
    if allowed and str(item.inventory_kind) not in allowed:
        raise ValueError(
            f"{item.identity} of kind {item.inventory_kind} "
            f"is not allowed in storage {storage.identity}"
        )


def validate_storage_child(
    parent: StorageCollection, child: InventoryImplementation | StorageCollection
) -> None:
    """Validate a direct edge in the fridge/shelf hierarchy."""
    if not isinstance(parent, StorageCollection):
        raise ValueError("Storage parent must be a StorageCollection")

    parent_kind = str(parent.storage_kind)
    if parent_kind not in STORAGE_KINDS:
        raise ValueError(f"Unknown storage kind: {parent_kind}")

    if isinstance(child, StorageCollection):
        allowed = set(parent.allowed_storage_kinds)
        if not allowed:
            raise ValueError(
                f"Storage {parent.identity} does not allow child storage collections"
            )
        if str(child.storage_kind) not in allowed:
            raise ValueError(
                f"Storage kind {child.storage_kind} is not allowed in {parent.identity}"
            )
        return

    if isinstance(child, InventoryImplementation):
        validate_placement(child, parent)
        return

    raise ValueError("Storage children must be StorageCollection or InventoryImplementation")


def validate_well_position(well: str) -> str:
    """Validate and normalize a 96-well location (A1-H12)."""
    if not isinstance(well, str):
        raise ValueError("Well must be provided as a string like 'A1'")

    normalized = well.strip().upper()
    if not WELL_96_RE.match(normalized):
        raise ValueError(
            f"Invalid 96-well position '{well}'. Expected rows A-H and columns 1-12."
        )
    return normalized


def validate_container_spec(rows: Sequence[str], columns: Iterable[int]) -> tuple[list[str], list[int]]:
    """Validate row/column layout declaration for a container."""
    if not rows:
        raise ValueError("Container must define at least one allowed row")

    normalized_rows = [str(r).strip().upper() for r in rows]
    if any(not r.isalpha() or len(r) != 1 for r in normalized_rows):
        raise ValueError("Rows must be single alphabetic labels like ['A', 'B']")

    normalized_cols = [int(c) for c in columns]
    if not normalized_cols:
        raise ValueError("Container must define at least one allowed column")
    if any(c < 1 for c in normalized_cols):
        raise ValueError("Columns must be positive integers")

    return normalized_rows, normalized_cols


def validate_container_position(
    container: InventoryImplementation, row: str, column: int
) -> tuple[str, int]:
    """Validate a row/column placement against a container's allowed positions."""
    normalized_row = str(row).strip().upper()
    normalized_col = int(column)

    if normalized_row not in list(container.allowed_rows):
        raise ValueError(
            f"Row {normalized_row} is not allowed in container {container.identity}; "
            f"allowed rows: {list(container.allowed_rows)}"
        )
    if normalized_col not in list(container.allowed_columns):
        raise ValueError(
            f"Column {normalized_col} is not allowed in container {container.identity}; "
            f"allowed columns: {list(container.allowed_columns)}"
        )

    return normalized_row, normalized_col


def validate_container_and_item(
    container: InventoryImplementation,
    item: InventoryImplementation,
) -> None:
    """Validate implementation-to-container semantics."""
    if not isinstance(container, InventoryImplementation):
        raise ValueError("Container must be an InventoryImplementation")
    if not isinstance(item, InventoryImplementation):
        raise ValueError("Item must be an InventoryImplementation")

    kind = str(container.inventory_kind)
    if kind not in CONTAINER_KINDS:
        raise ValueError(
            f"Container {container.identity} must be one of {sorted(CONTAINER_KINDS)}"
        )


def validate_inventory_graph(doc) -> None:
    """Validate inventory-specific invariants that SBOL core does not express.

    SBOL validates the RDF structure, while this function validates the physical
    location model: direct storage membership, inverse links, coordinates, and
    slot occupancy.
    """
    direct_parent: dict[str, str] = {}
    occupied_slots: set[tuple[str, str, int]] = set()

    for storage in doc.collections:
        if not isinstance(storage, StorageCollection):
            raise ValueError(f"{storage.identity} is not a StorageCollection")
        if str(storage.storage_kind) not in STORAGE_KINDS:
            raise ValueError(f"Unknown storage kind: {storage.storage_kind}")

        member_uris = [str(member) for member in storage.members]
        if len(member_uris) != len(set(member_uris)):
            raise ValueError(f"Storage {storage.identity} has duplicate members")

        for member_uri in member_uris:
            child = doc.find(member_uri)
            if child is None:
                raise ValueError(
                    f"Storage {storage.identity} references missing member {member_uri}"
                )
            if not isinstance(child, (StorageCollection, InventoryImplementation)):
                raise ValueError(
                    f"Storage {storage.identity} member {member_uri} is not inventory data"
                )
            validate_storage_child(storage, child)
            if member_uri in direct_parent:
                raise ValueError(
                    f"{member_uri} has multiple direct storage parents: "
                    f"{direct_parent[member_uri]} and {storage.identity}"
                )
            direct_parent[member_uri] = str(storage.identity)

            inverse_parent = (
                child.parent_storage
                if isinstance(child, StorageCollection)
                else child.stored_at
            )
            if str(inverse_parent) != str(storage.identity):
                raise ValueError(
                    f"Inverse storage link for {member_uri} does not match member parent "
                    f"{storage.identity}"
                )

    for storage in doc.collections:
        parent_uri = str(storage.parent_storage) if storage.parent_storage else None
        if parent_uri and direct_parent.get(str(storage.identity)) != parent_uri:
            raise ValueError(
                f"Storage {storage.identity} has parentStorage without matching membership"
            )

    for item in doc.implementations:
        if not isinstance(item, InventoryImplementation):
            raise ValueError(f"{item.identity} is not an InventoryImplementation")
        validate_item(item)

        container_uri = str(item.contained_in_container) if item.contained_in_container else None
        row = str(item.container_row) if item.container_row is not None else None
        column = int(item.container_column) if item.container_column is not None else None
        coordinate_values = (container_uri, row, column)
        if any(value is not None for value in coordinate_values) and any(
            value is None for value in coordinate_values
        ):
            raise ValueError(
                f"{item.identity} must have container, row, and column together"
            )

        if container_uri is not None:
            container = doc.find(container_uri)
            if not isinstance(container, InventoryImplementation):
                raise ValueError(f"{item.identity} refers to a missing container {container_uri}")
            validate_container_and_item(container, item)
            validate_container_position(container, row, column)
            slot = (container_uri, row, column)
            if slot in occupied_slots:
                raise ValueError(f"Container position {row}{column} in {container_uri} is occupied")
            occupied_slots.add(slot)
            if str(item.identity) in direct_parent or item.stored_at is not None:
                raise ValueError(
                    f"Contained item {item.identity} cannot also have direct storage membership"
                )
        elif item.stored_at is not None:
            if direct_parent.get(str(item.identity)) != str(item.stored_at):
                raise ValueError(
                    f"Item {item.identity} has storedAt without matching storage membership"
                )
