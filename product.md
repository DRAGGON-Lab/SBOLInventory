# Product definition

## Name
SBOLInventory

## Purpose
SBOLInventory provides a Python API for modeling physical laboratory inventory in SBOL 2 with explicit distinction between storage hierarchy and container occupancy.

## Core model

- Storage hierarchy (`Collection`):
  - `FridgeMinus80C`
  - `FridgeMinus20C`
  - `Fridge4C`
  - `Shelf`
- Physical implementations (`Implementation`):
  - `Box`
  - `SolidMediaPlate`
  - `BacterialStock`
  - `DilutedPlasmid`
  - `ProcuredMaterial`
  - `PlatedStrain`

## Functional requirements

1. Container implementations (`Box`, `SolidMediaPlate`) must declare allowed rows and columns.
2. Placement into containers must require row/column and validate:
   - valid row/column for that container
   - target position not already occupied
3. Item lifecycle support:
   - move between containers
   - remove from container
   - discard item by setting active flag to false
4. Designs (`ModuleDefinition`) are never directly placed; only implementations are placed.
