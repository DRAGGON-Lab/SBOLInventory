# Product definition

## Name
SBOLInventory

## Purpose
SBOLInventory provides a clean Python API for modeling laboratory inventory in SBOL 2 so that physical samples can be represented, placed into storage hierarchies, and later exchanged or submitted through tools such as SynBioHub.

## Problem
Laboratories often have a digital design representation, but the physical realization of those designs is tracked outside the design graph, often in spreadsheets or ad hoc notes.

SBOL already includes `Implementation` as the concept for physical realization, but practical laboratory inventory tracking needs more structure than the base class provides. We need a reusable software layer that can:

- represent implementation type
- capture storage location
- organize storage containers hierarchically
- capture plate well occupancy relative to a specific plate
- validate whether an item is placed in an allowed storage location

## Users
Primary users:

- synthetic biology software engineers
- laboratory informatics developers
- SynBioHub integrators
- researchers building physical sample tracking pipelines

## MVP
The first release of SBOLInventory should support:

- custom SBOL extension-aware classes for inventory objects and storage collections
- controlled vocabulary constants for item and storage kinds
- factory functions for:
  - `ExtractedPlasmid`
  - `BacterialStock`
  - `SolidMediaPlate`
  - `FridgeMinus80C`
  - `FridgeMinus20C`
  - `Fridge4C`
  - `Shelf`
  - `Box`
- plate placement helper (`place_in_plate`) using well strings like `A1`
- placement and well validation
- basic document assembly
- example notebook demonstrating common workflows

## Non-goals
This repository should not initially include:

- SynBioHub login and submission code
- HTTP APIs
- database persistence
- machine learning
- image attachment handling
- frontend code

## Functional requirements

### FR1: inventory object creation
The package must support creation of typed SBOL implementations for:
- extracted plasmid
- bacterial stock
- solid media plate

### FR2: storage hierarchy creation
The package must support creation of storage nodes for:
- freezer or fridge
- shelf
- box

### FR3: containment modeling
The package must support representing:
- freezer contains shelf
- shelf contains box
- box contains item (e.g., plate)
- plate contains inventory implementation at a relative well (`plate_location`)

### FR4: placement validation
The package must support application-level validation rules:
- extracted plasmids go to -20 C
- bacterial stocks go to -80 C
- solid media plates go to 4 C storage
- plate wells validate against the 96-well domain (`A1` to `H12`)

### FR5: examples
The repository must include examples that are easy for humans and AI coding agents to execute and extend.

## Quality goals
- simple API
- explicit naming
- low cognitive load
- easy import into a future backend service
- easily testable
- faithful to the intended inventory model
