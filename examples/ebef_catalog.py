"""A public-data SBOL 3 catalog of Caltech's EBEF.

This is an architectural example, not an operational source of truth. It is
derived from the public EBEF equipment page, with separately cited manufacturer
limits and illumination specifications. It intentionally omits serial
numbers, network addresses, booking state, calibration, private room details,
and claims that an instrument is executable through any workflow system.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import sbol3

from sbol_inventory import (
    ABSORBANCE_MEASUREMENT,
    ANAEROBIC_ENVIRONMENT_CONTROL,
    BIOSAFETY_CONTAINMENT,
    CENTRIFUGATION,
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
    STORAGE_ZONE,
    THERMAL_CYCLING,
    WATER_PURIFICATION,
    WORK_AREA,
    WORKSTATION,
    Capability,
    PropertyValue,
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
SOURCE_ACCESSED = "2026-10-02"
EPOCH_SOURCE = "https://www.agilent.com/cs/library/packageinsert/public/Epoch2_IFU_1771011IAW.C.pdf"
PROFLEX_SOURCE = (
    "https://assets.thermofisher.com/TFS-Assets/LSG/Specification-Sheets/"
    "proflex-pcr-system-specification-sheet.pdf"
)
AZURE_SOURCE = "https://azurebiosystems.com/products/azure-imaging-systems/azure-300/"
DEFAULT_NAMESPACE = "https://example.org/ebef/"
PROPERTY = "https://example.org/ebef/property/"
OM = "http://www.ontology-of-units-of-measure.org/resource/om-2/"
DEG_C = OM + "degreeCelsius"
PERCENT = OM + "percent"
KELVIN = OM + "kelvin"
DEG_C_PER_SECOND = OM + "degreeCelsiusPerSecond-Time"
MILLILITRE = OM + "millilitre"
FOOT = OM + "foot-International"


def described(kind: str, *parameters: PropertyValue) -> Capability:
    """A publicly described capability with an unverified invocation path."""

    return make_capability(
        kind,
        qualification=QUALIFICATION_DESCRIBED,
        control_mode=CONTROL_UNSPECIFIED,
        parameters=list(parameters),
    )


def prop(
    name: str, value: str | int | float | bool, unit: str | None = None, *, source: str = SOURCE
) -> PropertyValue:
    """Use OM-2 units and retain the source of each individual fact."""

    property_value = make_property(PROPERTY + name, value, unit=unit)
    property_value.derived_from = [source]
    return property_value


def build_ebef_catalog(namespace: str = DEFAULT_NAMESPACE) -> sbol3.Document:
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
        description=(
            "Separate refrigerators and freezers operate at 4, -20, and -70 degrees Celsius. "
            "Individual units and counts are unpublished."
        ),
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
        kind=INSTRUMENT,
        located_in=chamber_1_interior,
        manufacturer="Hamilton",
        model="Microlab Prep",
        capabilities=[
            described(
                LIQUID_HANDLING,
                prop("supported_plate_wells", 96),
                prop("supports_serial_dilution", True),
            )
        ],
        name="Anaerobic liquid handler",
    )
    potentiostat = make_asset(
        ns + "potentiostat_96_well",
        kind=INSTRUMENT,
        located_in=chamber_1_interior,
        capabilities=[
            described(
                ELECTROCHEMICAL_MEASUREMENT,
                prop("supported_plate_wells", 96),
            )
        ],
        name="96-well potentiostat",
    )
    chamber_2_centrifuge = make_asset(
        ns + "anaerobic_swinging_bucket_centrifuge",
        kind=INSTRUMENT,
        located_in=chamber_2_interior,
        capabilities=[described(CENTRIFUGATION)],
        name="Anaerobic swinging-bucket centrifuge",
    )

    dragonfly = make_asset(
        ns + "dragonfly_confocal",
        kind=INSTRUMENT,
        located_in=microscopy,
        model="Dragonfly spinning disk confocal",
        capabilities=[
            described(
                CONFOCAL_MICROSCOPY,
                prop("camera_pixels_x", 2048),
                prop("camera_pixels_y", 2048),
                prop("supports_timelapse", True),
            )
        ],
        name="Dragonfly spinning disk confocal microscope",
    )
    plasma_cleaner = make_asset(
        ns + "plasma_cleaner",
        kind=INSTRUMENT,
        located_in=microscopy,
        capabilities=[described(PLASMA_CLEANING)],
        name="Plasma cleaner",
    )

    shaking_incubator_1 = make_asset(
        ns + "eppendorf_s44i_1",
        kind=INSTRUMENT,
        located_in=microbiology,
        manufacturer="Eppendorf",
        model="S44i",
        capabilities=[
            described(
                SHAKING_INCUBATION,
                prop("supports_refrigeration", False),
                prop("minimum_temperature", 30.0, DEG_C),
            )
        ],
        name="Shaking incubator 1 (top, heating only)",
    )
    shaking_incubator_2 = make_asset(
        ns + "eppendorf_s44i_2",
        kind=INSTRUMENT,
        located_in=microbiology,
        manufacturer="Eppendorf",
        model="S44i",
        capabilities=[
            described(
                SHAKING_INCUBATION,
                prop("supports_refrigeration", True),
                prop("supports_photosynthetic_lighting", True),
            )
        ],
        name="Shaking incubator 2 (refrigerated)",
    )
    shaking_incubator_3 = make_asset(
        ns + "eppendorf_s44i_3",
        kind=INSTRUMENT,
        located_in=microbiology,
        manufacturer="Eppendorf",
        model="S44i",
        capabilities=[
            described(
                SHAKING_INCUBATION,
                prop("supports_refrigeration", True),
                prop("supports_photosynthetic_lighting", True),
            )
        ],
        name="Shaking incubator 3 (refrigerated)",
    )
    static_incubator = make_asset(
        ns + "static_incubator_group",
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
        kind=INSTRUMENT,
        located_in=microbiology,
        manufacturer="Agilent BioTek",
        model="Epoch 2",
        capabilities=[
            described(
                ABSORBANCE_MEASUREMENT,
                prop("supported_plate_wells", 96),
            ),
            described(
                INCUBATION,
                prop("minimum_temperature", 18.0, DEG_C, source=EPOCH_SOURCE),
                prop("maximum_temperature", 65.0, DEG_C),
                prop("minimum_temperature_above_ambient", 4.0, KELVIN, source=EPOCH_SOURCE),
            ),
        ],
        name="Epoch 2 plate reader",
        description="The facility reports absorbance only, with no fluorescence detection.",
    )

    proflex = make_asset(
        ns + "proflex",
        kind=INSTRUMENT,
        located_in=microbiology,
        model="ProFlex PCR System",
        name="ProFlex thermocycler",
        description="Composite parent; independently runnable blocks are child assets.",
    )
    proflex_blocks = [
        make_asset(
            ns + f"proflex_block_{index}",
            kind=FUNCTIONAL_UNIT,
            part_of=proflex,
            capabilities=[
                described(
                    THERMAL_CYCLING,
                    prop("independently_controlled_temperature_zones", 2),
                    prop("well_count", 32, source=PROFLEX_SOURCE),
                    prop("nominal_tube_volume", 0.2, MILLILITRE, source=PROFLEX_SOURCE),
                    prop("minimum_temperature", 0.0, DEG_C, source=PROFLEX_SOURCE),
                    prop("maximum_temperature", 100.0, DEG_C, source=PROFLEX_SOURCE),
                    prop("maximum_block_ramp_rate", 6.0, DEG_C_PER_SECOND, source=PROFLEX_SOURCE),
                    prop("maximum_sample_ramp_rate", 4.4, DEG_C_PER_SECOND, source=PROFLEX_SOURCE),
                )
            ],
            name=f"ProFlex independent block {index}",
        )
        for index in range(1, 4)
    ]

    gel_imager = make_asset(
        ns + "azure_300",
        kind=INSTRUMENT,
        located_in=microbiology,
        model="Azure 300",
        capabilities=[
            described(
                GEL_IMAGING,
                prop("model_supports_uv_illumination", True, source=AZURE_SOURCE),
                prop("model_supports_blue_light_illumination", True, source=AZURE_SOURCE),
            )
        ],
        name="Gel imager",
    )
    electrophoresis = make_asset(
        ns + "electrophoresis_station",
        kind=WORKSTATION,
        located_in=microbiology,
        capabilities=[described(ELECTROPHORESIS)],
        name="DNA and protein electrophoresis station",
    )
    media_prep_station = make_asset(
        ns + "media_prep_station",
        kind=WORKSTATION,
        located_in=media_prep,
        capabilities=[
            described(MEDIA_PREPARATION),
            described(PH_MEASUREMENT),
            described(WATER_PURIFICATION),
        ],
        name="Media and buffer preparation station",
    )
    main_bsc = make_asset(
        ns + "main_biosafety_cabinet",
        kind=INSTRUMENT,
        located_in=microbiology,
        capabilities=[
            described(
                BIOSAFETY_CONTAINMENT,
                prop("nominal_cabinet_width", 6.0, FOOT),
            )
        ],
        name="Main-lab biosafety cabinet",
    )
    main_autoclave = make_asset(
        ns + "amsco_630ls",
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
                )
            ],
            name=name,
        )
        plant_chamber_zones.append(interior)
        plant_chambers.append(chamber)

    plant_bsc = make_asset(
        ns + "plant_biosafety_cabinet",
        kind=INSTRUMENT,
        located_in=plant_lab,
        capabilities=[
            described(
                BIOSAFETY_CONTAINMENT,
                prop("nominal_cabinet_width", 4.0, FOOT),
            )
        ],
        name="Plant-lab biosafety cabinet",
    )
    plant_autoclave = make_asset(
        ns + "plant_autoclave",
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
            shaking_incubator_1,
            shaking_incubator_2,
            shaking_incubator_3,
            static_incubator,
            epoch,
            proflex,
            *proflex_blocks,
            gel_imager,
            electrophoresis,
            media_prep_station,
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
