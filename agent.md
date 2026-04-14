# agent.md

## Role
You are the software engineering agent for `SBOLInventory`.

## Current intended model

- Use `StorageCollection` for fridges and shelves.
- Use `InventoryImplementation` for physical containers/items including:
  - `Box`, `SolidMediaPlate`, `BacterialStock`, `DilutedPlasmid`, `ProcuredMaterial`, `PlatedStrain`.
- Container implementations must define allowed rows/columns.
- Placing implementations into containers must validate coordinate validity and occupancy.
- Implementations support lifecycle state (`is_active`) and discard action.

## Design rule
- Do not place `ModuleDefinition` directly in containers.
- Place only implementations whose `built` points to the design.
