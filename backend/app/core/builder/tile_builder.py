import subprocess
import json
import os
import time
from core.pipeline.parquet_loader import load_layer
from core.pipeline.features import build_feature
from utils.logger import get_logger

logger = get_logger(__name__)


def build_pmtiles(parquet_path: str, output_path: str, category: str, mode: str):
    start_time = time.time()

    logger.info(f"Building PMTiles for category={category}, mode={mode}")

    rows = load_layer(parquet_path, category, mode)

    logger.info(f"Data loaded in {time.time() - start_time:.2f}s")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # ✅ TEMP FILE (THIS IS THE FIX)
    tmp_file = f"/tmp/{category}_{mode}.geojsonl"

    count = 0
    invalid = 0

    logger.info("Writing GeoJSONL file...")

    with open(tmp_file, "w") as f:
        for h3_index, value in rows:
            try:
                feature = build_feature(h3_index, value)
            except Exception as e:
                invalid += 1
                logger.error(f"Feature build failed: {e}")
                continue

            if not isinstance(feature, dict):
                invalid += 1
                continue

            if "geometry" not in feature or feature["geometry"] is None:
                invalid += 1
                continue

            f.write(json.dumps(feature) + "\n")
            count += 1

    logger.info(f"Features written: {count}, invalid: {invalid}")

    if count == 0:
        raise RuntimeError("No valid features generated")

    logger.info("Running tippecanoe...")

    cmd = [
        
        "tippecanoe",
        tmp_file,
        "-o", output_path,
        "-l", f"{category}_{mode}",
        "-Z5", "-z14",
        "--coalesce-densest-as-needed", #"--drop-densest-as-needed",
        "--no-feature-limit",
        "--no-tile-size-limit", #may cause memory issues, but we want to keep all features
        "--no-line-simplification",
        "--extend-zooms-if-still-dropping",
        "--force"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    logger.info(f"Total time: {time.time() - start_time:.2f}s")

    if result.returncode != 0:
        raise RuntimeError(f"Tippecanoe failed:\n{result.stderr}")