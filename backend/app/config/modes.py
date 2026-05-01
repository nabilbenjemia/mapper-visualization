from enum import Enum

class Mode(str, Enum):
    walk = "walk"
    bike = "bike"
    drive = "drive"
    transit = "transit"
    transit_bus = "transit_bus"
    transit_rail = "transit_rail"
    walk_transit = "walk_transit"
    walk_transit_bus = "walk_transit_bus"
    walk_transit_rail = "walk_transit_rail"
    
def get_available_modes():
    return [mode.value for mode in Mode]

MODES = [m.value for m in Mode]