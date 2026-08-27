"""A public-data SBOL 3 catalog of Caltech's EBEF.

This is an architectural example, not an operational source of truth. It is
derived only from the public EBEF equipment page and intentionally omits serial
numbers, network addresses, booking state, calibration, private room details,
and claims that an instrument is executable through any workflow system.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from sbol_inventory import (
    ABSORBANCE_MEASUREMENT,
    ANAEROBIC_ENVIRONMENT_CONTROL,
    BIOSAFETY_CONTAINMENT,
    CENTRIFUGATION,
    COLD_STORAGE,
    CONFOCAL_MICROSCOPY,
    CONTAINMENT_ZONE,
    CONTROL_UNSPECIFIED,
    ELECTROCHEMICAL_MEASUREMENT,
    ELECTROPHORESIS,
    ENVIRONMENT_CONTROLLER,
    ENVIRONMENT_ZONE,
    FUNCTIONAL_UNIT,
    GEL_IMAGING,
    INCUBATION,
    INSTRUMENT,
    LIQUID_HANDLING,
    MEDIA_PREPARATION,
    PH_MEASUREMENT,
    PLANT_GROWTH,
    PLASMA_CLEANING,
    QUALIFICATION_DESCRIBED,
    ROOM,
    SHAKING_INCUBATION,
    STATIC_INCUBATION,
    STEAM_STERILIZATION,
    STORAGE_ASSET,
    STORAGE_ZONE,
    THERMAL_CYCLING,
    WATER_PURIFICATION,
    WORK_AREA,
    WORKSTATION,
    add_all,
    make_asset,
    make_capability,
    make_document,
    make_facility,
    make_property,
    make_zone,
    write_turtle,
)

SOURCE = (
    "https://resnick.caltech.edu/resource-centers/ecology-and-biosphere-engineering-facility-ebef"
)
SOURCE_ACCESSED = "2026-08-26"
DEFAULT_NAMESPACE = "https://example.org/ebef/"
PROPERTY = "https://example.org/ebef/property/"
DEG_C = "http://qudt.org/vocab/unit/DEG_C"
PERCENT = "http://qudt.org/vocab/unit/PERCENT"


def described(kind: str, *parameters, control_mode: str = CONTROL_UNSPECIFIED):
    """A capability evidenced by the public page but not yet commissioned."""

    return make_capability(
        kind,
        qualification=QUALIFICATION_DESCRIBED,
        control_mode=control_mode,
        parameters=list(parameters),
    )


def prop(name: str, value, unit: str | None = None):
    return make_property(PROPERTY + name, value, unit=unit)


def build_ebef_catalog(namespace: str = DEFAULT_NAMESPACE):
    """Build an EBEF-shaped catalog from the facility's public equipment page."""

    ns = namespace.rstrip("/") + "/"
    document = make_document()
    ebef = make_facility(
        ns + "facility",
        name="Resnick Ecology and Biosphere Engineering Facility",
        description=(
            "Public-data example catalog for a multi-user BSL2+ microbiology, "
            "microscopy, and plant cultivation facility; source accessed "
            f"{SOURCE_ACCESSED}."
        ),
    )
    ebef.derived_from = [SOURCE]

    basement_main_lab = make_zone(
        ns + "basement_main_lab",
        facility=ebef,
        kind=ROOM,
        name="Main lab (basement)",
    )
    microbiology = make_zone(
        ns + "microbiology_lab",
        facility=ebef,
        parent_zone=basement_main_lab,
        kind=WORK_AREA,
        name="Microbiology lab (basement)",
    )
    microscopy = make_zone(
        ns + "microscopy_lab",
        facility=ebef,
        parent_zone=basement_main_lab,
        kind=WORK_AREA,
        name="Microscopy lab (basement)",
    )
    media_prep = make_zone(
        ns + "media_prep_room",
        facility=ebef,
        parent_zone=basement_main_lab,
        kind=WORK_AREA,
        name="Media preparation room",
    )
    freezer_room = make_zone(
        ns + "freezer_room",
        facility=ebef,
        parent_zone=basement_main_lab,
        kind=STORAGE_ZONE,
        name="Freezer room",
    )
    plant_lab = make_zone(
        ns + "plant_lab",
        facility=ebef,
        kind=ROOM,
        name="Plant lab (first floor)",
    )
    chamber_1_interior = make_zone(
        ns + "anaerobic_chamber_1_interior",
        facility=ebef,
        parent_zone=microbiology,
        kind=CONTAINMENT_ZONE,
        name="Anaerobic chamber 1 interior",
        conditions=[
            prop("nitrogen_fraction", 95.0, PERCENT),
            prop("hydrogen_fraction", 5.0, PERCENT),
            prop("maximum_added_co2", 20.0, PERCENT),
        ],
    )
    chamber_2_interior = make_zone(
        ns + "anaerobic_chamber_2_interior",
        facility=ebef,
        parent_zone=microbiology,
        kind=CONTAINMENT_ZONE,
        name="Anaerobic chamber 2 interior",
        conditions=[
            prop("nitrogen_fraction", 95.0, PERCENT),
            prop("hydrogen_fraction", 5.0, PERCENT),
            prop("maximum_added_co2", 20.0, PERCENT),
        ],
    )

    chamber_1 = make_asset(
        ns + "anaerobic_chamber_1",
        facility=ebef,
        kind=ENVIRONMENT_CONTROLLER,
        located_in=microbiology,
        establishes_zones=[chamber_1_interior],
        manufacturer="Coy Laboratory Products",
        model="Vinyl anaerobic chamber",
        capabilities=[described(ANAEROBIC_ENVIRONMENT_CONTROL)],
        name="Anaerobic chamber 1",
    )
    chamber_2 = make_asset(
        ns + "anaerobic_chamber_2",
        facility=ebef,
        kind=ENVIRONMENT_CONTROLLER,
        located_in=microbiology,
        establishes_zones=[chamber_2_interior],
        manufacturer="Coy Laboratory Products",
        model="Extra-wide vinyl anaerobic chamber",
        capabilities=[described(ANAEROBIC_ENVIRONMENT_CONTROL)],
        name="Anaerobic chamber 2",
    )

    microlab_prep = make_asset(
        ns + "microlab_prep",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=chamber_1_interior,
        manufacturer="Hamilton",
        model="Microlab Prep",
        capabilities=[
            described(
                LIQUID_HANDLING,
                prop("supported_plate_wells", 96),
                prop("supports_serial_dilution", True),
                control_mode=CONTROL_UNSPECIFIED,
            )
        ],
        name="Anaerobic liquid handler",
    )
    potentiostat = make_asset(
        ns + "potentiostat_96_well",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=chamber_1_interior,
        capabilities=[
            described(
                ELECTROCHEMICAL_MEASUREMENT,
                prop("supported_plate_wells", 96),
                control_mode=CONTROL_UNSPECIFIED,
            )
        ],
        name="96-well potentiostat",
    )
    chamber_2_centrifuge = make_asset(
        ns + "anaerobic_swinging_bucket_centrifuge",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=chamber_2_interior,
        capabilities=[described(CENTRIFUGATION)],
        name="Anaerobic swinging-bucket centrifuge",
    )

    dragonfly = make_asset(
        ns + "dragonfly_confocal",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microscopy,
        model="Dragonfly spinning disk confocal",
        capabilities=[
            described(
                CONFOCAL_MICROSCOPY,
                prop("camera_pixels_x", 2048),
                prop("camera_pixels_y", 2048),
                prop("supports_timelapse", True),
                control_mode=CONTROL_UNSPECIFIED,
            )
        ],
        name="Dragonfly spinning disk confocal microscope",
    )
    plasma_cleaner = make_asset(
        ns + "plasma_cleaner",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microscopy,
        capabilities=[described(PLASMA_CLEANING)],
        name="Plasma cleaner",
    )

    shaking_incubators = []
    for index in range(1, 4):
        refrigerates = index in {2, 3}
        parameters = [
            prop("supports_refrigeration", refrigerates),
            prop("supports_photosynthetic_lighting", refrigerates),
        ]
        if index == 1:
            parameters.append(prop("minimum_temperature", 30.0, DEG_C))
        shaking_incubators.append(
            make_asset(
                ns + f"eppendorf_s44i_{index}",
                facility=ebef,
                kind=INSTRUMENT,
                located_in=microbiology,
                manufacturer="Eppendorf",
                model="S44i",
                capabilities=[
                    described(
                        SHAKING_INCUBATION,
                        *parameters,
                        control_mode=CONTROL_UNSPECIFIED,
                    )
                ],
                name=f"Shaking incubator {index}",
            )
        )
    static_incubator = make_asset(
        ns + "static_incubator_group",
        facility=ebef,
        kind=WORKSTATION,
        located_in=microbiology,
        capabilities=[
            described(
                STATIC_INCUBATION,
                prop("minimum_temperature", 17.0, DEG_C),
                prop("maximum_temperature", 70.0, DEG_C),
            )
        ],
        name="Static incubators",
        description="Public page describes several units; individual asset IDs are not public.",
    )

    epoch = make_asset(
        ns + "biotek_epoch_2",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microbiology,
        manufacturer="Agilent BioTek",
        model="Epoch 2",
        capabilities=[
            described(
                ABSORBANCE_MEASUREMENT,
                prop("supported_plate_wells", 96),
                prop("supports_fluorescence", False),
                control_mode=CONTROL_UNSPECIFIED,
            ),
            described(
                INCUBATION,
                prop("maximum_temperature", 65.0, DEG_C),
                control_mode=CONTROL_UNSPECIFIED,
            ),
        ],
        name="Epoch 2 plate reader",
    )

    proflex = make_asset(
        ns + "proflex",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microbiology,
        model="ProFlex PCR System",
        name="ProFlex thermocycler",
        description="Composite parent; independently runnable blocks are child assets.",
    )
    proflex_blocks = [
        make_asset(
            ns + f"proflex_block_{index}",
            facility=ebef,
            kind=FUNCTIONAL_UNIT,
            part_of=proflex,
            capabilities=[
                described(
                    THERMAL_CYCLING,
                    prop("temperature_zones", 2),
                    control_mode=CONTROL_UNSPECIFIED,
                )
            ],
            name=f"ProFlex independent block {index}",
        )
        for index in range(1, 4)
    ]

    gel_imager = make_asset(
        ns + "azure_300",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microbiology,
        model="Azure 300",
        capabilities=[described(GEL_IMAGING, control_mode=CONTROL_UNSPECIFIED)],
        name="Gel imager",
    )
    electrophoresis = make_asset(
        ns + "electrophoresis_station",
        facility=ebef,
        kind=WORKSTATION,
        located_in=microbiology,
        capabilities=[described(ELECTROPHORESIS)],
        name="DNA and protein electrophoresis station",
    )
    media_prep_station = make_asset(
        ns + "media_prep_station",
        facility=ebef,
        kind=WORKSTATION,
        located_in=media_prep,
        capabilities=[
            described(MEDIA_PREPARATION),
            described(PH_MEASUREMENT),
            described(WATER_PURIFICATION),
        ],
        name="Media and buffer preparation station",
    )
    cold_storage = make_asset(
        ns + "cold_storage_group",
        facility=ebef,
        kind=STORAGE_ASSET,
        located_in=freezer_room,
        capabilities=[
            described(
                COLD_STORAGE,
                prop("documented_temperatures", "4 C, -20 C, and -70 C"),
            )
        ],
        name="Publicly documented cold-storage units",
        description="Placeholder group pending identifiers for each reservable unit.",
    )
    main_bsc = make_asset(
        ns + "main_biosafety_cabinet",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microbiology,
        capabilities=[described(BIOSAFETY_CONTAINMENT, prop("width_feet", 6.0))],
        name="Main-lab biosafety cabinet",
    )
    main_autoclave = make_asset(
        ns + "amsco_630ls",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=microbiology,
        model="AMSCO 630LS",
        capabilities=[described(STEAM_STERILIZATION)],
        name="Large basement autoclave",
    )

    plant_chamber_specs = [
        ("conviron_gen1000_1", "Gen1000", "Plant chamber Gen1000 1"),
        ("conviron_gen1000_2", "Gen1000", "Plant chamber Gen1000 2"),
        ("conviron_gen2000", "Gen2000", "Plant chamber Gen2000"),
        ("conviron_gr48", "GR48", "Walk-in plant chamber"),
    ]
    plant_chamber_zones = []
    plant_chambers = []
    for identity, model, name in plant_chamber_specs:
        interior = make_zone(
            ns + identity + "_interior",
            facility=ebef,
            parent_zone=plant_lab,
            kind=ENVIRONMENT_ZONE,
            name=name + " interior",
        )
        chamber = make_asset(
            ns + identity,
            facility=ebef,
            kind=ENVIRONMENT_CONTROLLER,
            located_in=plant_lab,
            establishes_zones=[interior],
            manufacturer="Conviron",
            model=model,
            capabilities=[
                described(
                    PLANT_GROWTH,
                    prop("programmable_temperature", True),
                    prop("programmable_light", True),
                    prop("additive_co2", True),
                    prop("additive_humidity", True),
                    control_mode=CONTROL_UNSPECIFIED,
                )
            ],
            name=name,
        )
        plant_chamber_zones.append(interior)
        plant_chambers.append(chamber)

    plant_bsc = make_asset(
        ns + "plant_biosafety_cabinet",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=plant_lab,
        capabilities=[described(BIOSAFETY_CONTAINMENT, prop("width_feet", 4.0))],
        name="Plant-lab biosafety cabinet",
    )
    plant_autoclave = make_asset(
        ns + "plant_autoclave",
        facility=ebef,
        kind=INSTRUMENT,
        located_in=plant_lab,
        capabilities=[
            described(
                STEAM_STERILIZATION,
                prop("optional_effluent_decontamination", True),
            )
        ],
        name="Plant-lab soil and waste autoclave",
    )

    add_all(
        document,
        [
            ebef,
            basement_main_lab,
            microbiology,
            microscopy,
            media_prep,
            freezer_room,
            plant_lab,
            chamber_1_interior,
            chamber_2_interior,
            *plant_chamber_zones,
            chamber_1,
            chamber_2,
            microlab_prep,
            potentiostat,
            chamber_2_centrifuge,
            dragonfly,
            plasma_cleaner,
            *shaking_incubators,
            static_incubator,
            epoch,
            proflex,
            *proflex_blocks,
            gel_imager,
            electrophoresis,
            media_prep_station,
            cold_storage,
            main_bsc,
            main_autoclave,
            *plant_chambers,
            plant_bsc,
            plant_autoclave,
        ],
    )
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Turtle file to write")
    args = parser.parse_args()
    document = build_ebef_catalog()
    write_turtle(document, args.output)
    print(f"Wrote {len(document.objects)} SBOL objects to {args.output}")


if __name__ == "__main__":
    main()
