# Product definition

## Name
SBOLInventory

## Purpose
SBOLInventory provides a clean Python API for modeling laboratory inventory in SBOL 2 so physical samples and containers are represented as implementations linked to storage collections.

## Current model

- Storage hierarchy uses collections for environmental storage (`FridgeMinus80C`, `FridgeMinus20C`, `Fridge4C`, `Shelf`).
- `Box` and `SolidMediaPlate` are physical `InventoryImplementation` containers.
- Contained items are `InventoryImplementation` objects placed into containers with `row` + `column`.
- Placement is valid only when coordinates are allowed and currently unoccupied.
- Implementations include `active` status and can be discarded.

## Functional requirements

1. Create implementation kinds:
   - `DilutedPlasmid`
   - `BacterialStock`
   - `ProcuredMaterial`
   - `PlatedStrain`
   - `Box`
   - `SolidMediaPlate`
2. Create storage collections:
   - `FridgeMinus80C`
   - `FridgeMinus20C`
   - `Fridge4C`
   - `Shelf`
3. Place/move/remove implementations in box/plate containers using row/column coordinates.
4. Validate row/column coordinates and occupancy.
5. Discard implementations by setting active state false.
