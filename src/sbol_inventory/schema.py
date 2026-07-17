"""Extension-aware SBOL object definitions."""

from __future__ import annotations

import math
import re

import sbol2 as sbol
from sbol2 import Config

from .namespaces import EX, SBOL_COLLECTION, SBOL_IMPLEMENTATION


DISPLAY_ID_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _require_synbiohub_display_id(uri: str) -> None:
    """Avoid pySBOL2 treating a full URL as a display ID in SynBioHub mode."""
    homespace = Config.getHomespace().rstrip("/")
    if (
        homespace.startswith("https://synbiohub.org/")
        and Config.getOption("sbol_compliant_uris")
        and not DISPLAY_ID_RE.fullmatch(str(uri))
    ):
        raise ValueError(
            "SynBioHub configuration requires a display ID containing only "
            "letters, digits, and underscores; do not pass a full URI"
        )


class InventoryImplementation(sbol.Implementation):
    """Physical laboratory inventory item represented as an SBOL Implementation."""

    def __init__(self, uri: str = "example", version: str = "1"):
        _require_synbiohub_display_id(uri)
        super().__init__(uri=uri, version=version)

        self.inventory_kind = sbol.URIProperty(self, EX + "inventoryKind", 1, 1, [])
        self.stored_at = sbol.ReferencedObject(
            self, EX + "storedAt", SBOL_COLLECTION, 0, 1, []
        )
        self.contained_in_container = sbol.ReferencedObject(
            self, EX + "containedInContainer", SBOL_IMPLEMENTATION, 0, 1, []
        )
        self.container_row = sbol.TextProperty(
            self, EX + "containerRow", 0, 1, []
        )
        self.container_column = sbol.IntProperty(
            self, EX + "containerColumn", 0, 1, []
        )
        self.allowed_rows = sbol.TextProperty(
            self, EX + "allowedRows", 0, math.inf, []
        )
        self.allowed_columns = sbol.IntProperty(
            self, EX + "allowedColumns", 0, math.inf, []
        )
        self.is_active = sbol.IntProperty(
            self, EX + "isActive", 1, 1, []
        )
        self.barcode = sbol.TextProperty(self, EX + "barcode", 0, 1, [])
        self.lot_id = sbol.TextProperty(self, EX + "lotId", 0, 1, [])
        self.notes = sbol.TextProperty(self, EX + "notes", 0, 1, [])
        self.freeze_date = sbol.DateTimeProperty(self, EX + "freezeDate", 0, 1, [])

    def contained_object_uris(self) -> list[str]:
        """Return URIs for inventory objects currently contained by this object."""
        if self.doc is None:
            return []

        container_uri = str(self.identity)
        contained: list[str] = []
        for implementation in self.doc.implementations:
            if not isinstance(implementation, InventoryImplementation):
                continue
            if str(implementation.contained_in_container) == container_uri:
                contained.append(str(implementation.identity))
        return contained


class StorageCollection(sbol.Collection):
    """Storage hierarchy node represented as an SBOL Collection."""

    def __init__(self, uri: str = "example", version: str = "1"):
        _require_synbiohub_display_id(uri)
        super().__init__(uri=uri, version=version)

        self.storage_kind = sbol.URIProperty(self, EX + "storageKind", 1, 1, [])
        self.parent_storage = sbol.ReferencedObject(
            self, EX + "parentStorage", SBOL_COLLECTION, 0, 1, []
        )
        self.temperature_c = sbol.IntProperty(self, EX + "temperatureC", 0, 1, [])
        self.label = sbol.TextProperty(self, EX + "label", 0, 1, [])
        self.allowed_item_kinds = sbol.URIProperty(
            self, EX + "allowedItemKind", 0, math.inf, []
        )
        self.allowed_storage_kinds = sbol.URIProperty(
            self, EX + "allowedStorageKind", 0, math.inf, []
        )


def register_extensions() -> None:
    """Register pySBOL2 extension classes."""
    Config.register_extension_class(InventoryImplementation, SBOL_IMPLEMENTATION)
    Config.register_extension_class(StorageCollection, SBOL_COLLECTION)


register_extensions()
