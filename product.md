# Product definition

## Name
SBOLInventory

## Purpose
SBOLInventory provides a clean Python API for modeling laboratory inventory in SBOL 2 so that physical samples can be represented, placed into storage hierarchies, and later exchanged or submitted through tools such as SynBioHub.

## Problem
Laboratories often have a digital design representation, but the physical realization of those designs is tracked outside the design graph, often in spreadsheets or ad hoc notes.

SBOL already includes `Implementation` as the concept for physical realization, but practical laboratory inventory tracking needs more structure than the base class provides.

## Users
Primary users:

- synthetic biology software engineers
- laboratory informatics developers
- SynBioHub integrators
- researchers building physical sample tracking pipelines

## MVP
The package supports:

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
- plate placement helper: `place_in_plate(plate, item, well)`
- well validation for 96-well coordinates (`A1`-`H12`)
- basic document assembly
- example notebook demonstrating common workflows

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
- box contains item
- plate contains item by metadata on the item (`contained_in_plate`, `plate_location`)

### FR4: placement validation
The package must support application-level validation rules:
- extracted plasmids go to -20 C
- bacterial stocks go to -80 C
- solid media plates go to 4 C storage
- plate wells are restricted to valid 96-well coordinates

### FR5: examples
The repository must include examples that are easy for humans and AI coding agents to execute and extend.

## Semantics

- A `ModuleDefinition` is a design.
- A physical thing in inventory is an `InventoryImplementation`.
- Placing a strain in a plate means placing an implementation whose `built` points to the strain `ModuleDefinition`.
- Well coordinates are not global identifiers; they are meaningful only in context of a parent plate.
