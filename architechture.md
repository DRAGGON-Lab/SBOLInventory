# Architechture

## Overview
SBOLInventory is a small Python library organized around four layers:

1. **namespaces**
2. **schema**
3. **factories**
4. **validation**

An additional lightweight **document** helper module keeps common document assembly tasks centralized.

## Module structure

### `namespaces.py`
Contains:

- extension namespace URI
- SBOL class URIs
- controlled terms for inventory kinds
- controlled terms for storage kinds

This module is the single source of truth for vocabulary constants.

### `schema.py`
Contains the extension-aware object definitions:

- `InventoryImplementation`
- `StorageCollection`

Responsibilities:
- define extension properties
- register extension classes with pySBOL2
- keep the object model close to the prototype

### `factories.py`
Contains the construction helpers for domain objects:

- storage factories
- implementation factories
- containment helpers

Responsibilities:
- expose a concise API for creating typed objects
- reduce repeated boilerplate in user code
- keep client code readable

### `validation.py`
Contains semantic validation utilities:

- validate an individual item
- validate a placement relationship

Responsibilities:
- capture application rules without mixing them into constructors
- provide a clear extension point for stronger validation later

### `document.py`
Contains helpers for document-level operations such as:

- document creation
- bulk addition of top-level objects
- writing SBOL to disk

Responsibilities:
- avoid repeating common document assembly logic in notebooks and downstream services

## Design rationale

### Why extend `Implementation`
`Implementation` is the right semantic anchor for a physical realization of a design. The package preserves that meaning while adding inventory-specific annotations such as:

- `inventory_kind`
- `stored_at`
- `barcode`
- `lot_id`
- `notes`
- `freeze_date`

### Why extend `Collection`
The storage system is naturally hierarchical and grouping-oriented. `Collection` is therefore a good fit for representing:

- freezers
- shelves
- boxes
- slots

That keeps the storage layout explicit without inventing a second containment mechanism.

### Why keep validation separate
Constructors should create objects.
Validators should enforce policy.

This separation makes the package easier to reuse, test, and evolve. A future backend may choose to:
- reject invalid placements immediately
- warn but still create drafts
- apply additional project-specific policies

## Dependency flow

```text
namespaces -> schema -> factories -> validation
                      \-> document
```

The intended flow is one-way and simple. Higher-level modules import lower-level modules. Lower-level modules do not depend on higher-level orchestration logic.

## Example object graph

```text
FridgeMinus80C
└── Shelf
    └── Box
        └── Slot
            └── BacterialStock
```

## Future evolution
Likely future additions:

- richer validation against actual `built` object type
- serialization helpers beyond RDF/XML
- support for attachment metadata
- SynBioHub submission adapters
- richer querying utilities
