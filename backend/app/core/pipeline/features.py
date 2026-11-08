from core.pipeline.h3_to_geo import h3_to_geometry
from utils.logger import get_logger
import math

def build_feature(dataset: str, h3_index: str, value: float, round_value: int = 2):
    logger = get_logger(__name__, dataset)

    polygon, center = h3_to_geometry(h3_index)

    # sanitize value
    if value is None or (isinstance(value, float) and (math.isnan(value) or math.isinf(value))):
        logger.warning(f"Invalid value for {h3_index}, setting to 0.0")
        value = 0.0

    # validate geometry
    if not polygon:
        logger.error(f"No polygon for h3_index {h3_index}")
        return None

    return {
        "type": "Feature",
        "geometry": polygon,
        "properties": {
            "h3": h3_index,
            "value": round(value)
        }
    }
