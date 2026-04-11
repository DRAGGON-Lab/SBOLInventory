# agent.md

## Role
You are the software engineering agent for the `SBOLInventory` repository.

## Model guardrails

- Keep environmental storage (`Fridge*`, `Shelf`) collection-based.
- Keep physical containers and samples implementation-based.
- Never place a `ModuleDefinition` directly in storage or plate; use `InventoryImplementation` with `built` reference.
- Ensure container placement validates row/column constraints and occupancy.
- Keep lifecycle status explicit via the `active` field and discard helpers.
