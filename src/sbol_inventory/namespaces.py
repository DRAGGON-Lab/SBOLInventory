"""Stable vocabulary terms used by the SBOLInventory profile."""

INVENTORY_NS = "https://draggon.org/ns/inventory#"
FACILITY_NS = "https://draggon.org/ns/facility#"
CAPABILITY_NS = "https://draggon.org/ns/capability#"

# Backward-compatible name for the original extension namespace.
EX = INVENTORY_NS

# Facility extension classes.
FACILITY = FACILITY_NS + "Facility"
ZONE = FACILITY_NS + "Zone"
ASSET = FACILITY_NS + "Asset"
CAPABILITY_OFFERING = FACILITY_NS + "CapabilityOffering"
PROPERTY_VALUE = FACILITY_NS + "PropertyValue"

# General zone kinds. Applications may use additional stable IRIs.
ROOM = FACILITY_NS + "Room"
WORK_AREA = FACILITY_NS + "WorkArea"
CONTAINMENT_ZONE = FACILITY_NS + "ContainmentZone"
ENVIRONMENT_ZONE = FACILITY_NS + "EnvironmentZone"
STORAGE_ZONE = FACILITY_NS + "StorageZone"

# General asset kinds.
INSTRUMENT = FACILITY_NS + "Instrument"
CONTAINER = FACILITY_NS + "Container"
STORAGE_ASSET = FACILITY_NS + "StorageAsset"
FUNCTIONAL_UNIT = FACILITY_NS + "FunctionalUnit"
ENVIRONMENT_CONTROLLER = FACILITY_NS + "EnvironmentController"
WORKSTATION = FACILITY_NS + "Workstation"

# Existing material and labware vocabulary, retained as stable IRIs.
DILUTED_PLASMID = INVENTORY_NS + "DilutedPlasmid"
BACTERIAL_STOCK = INVENTORY_NS + "BacterialStock"
PLATED_STRAIN = INVENTORY_NS + "PlatedStrain"
PROCURED_MATERIAL = INVENTORY_NS + "ProcuredMaterial"

SOLID_MEDIA_PLATE = INVENTORY_NS + "SolidMediaPlate"
BOX = INVENTORY_NS + "Box"
FRIDGE_MINUS_80 = INVENTORY_NS + "FridgeMinus80C"
FRIDGE_MINUS_20 = INVENTORY_NS + "FridgeMinus20C"
FRIDGE_4C = INVENTORY_NS + "Fridge4C"
SHELF = INVENTORY_NS + "Shelf"

# Capability qualification is an ordered lifecycle. These values describe an
# offering at one facility, not an intrinsic property of the device model.
QUALIFICATION_DISCOVERED = FACILITY_NS + "Discovered"
QUALIFICATION_DESCRIBED = FACILITY_NS + "Described"
QUALIFICATION_PLANNABLE = FACILITY_NS + "Plannable"
QUALIFICATION_SIMULATABLE = FACILITY_NS + "Simulatable"
QUALIFICATION_EXECUTABLE = FACILITY_NS + "Executable"
QUALIFICATION_QUALIFIED = FACILITY_NS + "Qualified"

QUALIFICATION_ORDER = (
    QUALIFICATION_DISCOVERED,
    QUALIFICATION_DESCRIBED,
    QUALIFICATION_PLANNABLE,
    QUALIFICATION_SIMULATABLE,
    QUALIFICATION_EXECUTABLE,
    QUALIFICATION_QUALIFIED,
)

# How a capability is invoked at this facility.
CONTROL_UNSPECIFIED = FACILITY_NS + "UnspecifiedControl"
CONTROL_MANUAL = FACILITY_NS + "ManualControl"
CONTROL_REVIEWED_FILE = FACILITY_NS + "ReviewedFileControl"
CONTROL_API = FACILITY_NS + "ApiControl"
CONTROL_SILA2 = FACILITY_NS + "SiLA2Control"
CONTROL_OPC_UA = FACILITY_NS + "OpcUaControl"
CONTROL_VENDOR_SESSION = FACILITY_NS + "VendorSessionControl"

CONTROL_MODES = {
    CONTROL_UNSPECIFIED,
    CONTROL_MANUAL,
    CONTROL_REVIEWED_FILE,
    CONTROL_API,
    CONTROL_SILA2,
    CONTROL_OPC_UA,
    CONTROL_VENDOR_SESSION,
}

# Reusable capability kinds for examples and compiler adapters. The model
# accepts any stable capability IRI; this is deliberately not a closed device
# taxonomy. These terms describe operations, never product models.
LIQUID_HANDLING = CAPABILITY_NS + "LiquidHandling"
# Compatibility spelling for callers that describe the operation more narrowly.
LIQUID_TRANSFER = LIQUID_HANDLING
ABSORBANCE_MEASUREMENT = CAPABILITY_NS + "AbsorbanceMeasurement"
INCUBATION = CAPABILITY_NS + "Incubation"
SHAKING_INCUBATION = CAPABILITY_NS + "ShakingIncubation"
STATIC_INCUBATION = CAPABILITY_NS + "StaticIncubation"
SHAKING = CAPABILITY_NS + "Shaking"
THERMAL_CYCLING = CAPABILITY_NS + "ThermalCycling"
ENVIRONMENT_CONTROL = CAPABILITY_NS + "EnvironmentControl"
ANAEROBIC_ENVIRONMENT_CONTROL = CAPABILITY_NS + "AnaerobicEnvironmentControl"
CONFOCAL_MICROSCOPY = CAPABILITY_NS + "ConfocalMicroscopy"
PLASMA_CLEANING = CAPABILITY_NS + "PlasmaCleaning"
ELECTROCHEMICAL_MEASUREMENT = CAPABILITY_NS + "ElectrochemicalMeasurement"
GEL_IMAGING = CAPABILITY_NS + "GelImaging"
ELECTROPHORESIS = CAPABILITY_NS + "Electrophoresis"
CENTRIFUGATION = CAPABILITY_NS + "Centrifugation"
MEDIA_PREPARATION = CAPABILITY_NS + "MediaPreparation"
PH_MEASUREMENT = CAPABILITY_NS + "PhMeasurement"
WATER_PURIFICATION = CAPABILITY_NS + "WaterPurification"
BIOSAFETY_CONTAINMENT = CAPABILITY_NS + "BiosafetyContainment"
STEAM_STERILIZATION = CAPABILITY_NS + "SteamSterilization"
COLD_STORAGE = CAPABILITY_NS + "ColdStorage"
PLANT_GROWTH = CAPABILITY_NS + "PlantGrowth"

# PROV-O usage roles for run records.
RUN_ASSET = FACILITY_NS + "RunAsset"
RUN_INPUT_MATERIAL = FACILITY_NS + "RunInputMaterial"


__all__ = sorted(name for name in globals() if name.isupper() and not name.startswith("_"))
