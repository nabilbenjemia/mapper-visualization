import subprocess
import json
import os
import time
from core.pipeline.parquet_loader import load_layer
from core.pipeline.features import build_feature
from utils.logger import get_logger

logger = get_logger(__name__)

def build_pmtiles(parquet_paths: dict, output_path: str, category: str, mode: str):
    start_time = time.time()
    logger.info(f"Building PMTiles for category={category}, mode={mode}")

    zoom_config = {
        6:  {"min_zoom": 0,  "max_zoom": 6},
        8:  {"min_zoom": 7,  "max_zoom": 9},
        10: {"min_zoom": 10, "max_zoom": 14},
    }

    mbtiles_files = []

    for res, parquet_path in parquet_paths.items():
        logger.info(f"Processing resolution {res} with parquet {parquet_path}")
        rows = load_layer(parquet_path, category, mode)

        tmp_file = f"/tmp/{category}_{mode}_res{res}.geojsonl"
        tmp_mbtiles = f"/tmp/{category}_{mode}_res{res}.mbtiles"

        count = 0
        invalid = 0

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
                if count % 10000 == 0:
                    logger.info(f"Progress: {count} features written, {invalid} invalid")

        logger.info(f"Features written: {count}, invalid: {invalid}")

        if count == 0:
            logger.warning(f"No features for res {res}, skipping")
            continue

        zmin = zoom_config[res]["min_zoom"]
        zmax = zoom_config[res]["max_zoom"]

        extra_flags = ["--drop-densest-as-needed"] if res == 10 else []

        logger.info(f"Running tippecanoe for res {res}...")

        cmd = [
            "tippecanoe",
            tmp_file,                                           
            "-o", tmp_mbtiles,
            "-l", f"{category}_{mode}",
            f"-Z{zmin}",
            f"-z{zmax}",
            "--simplify-only-low-zooms",
            "--extend-zooms-if-still-dropping",
            "--force",
            *extra_flags
        ]

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

        out_lines = []
        for line in proc.stdout:
            out_lines.append(line.rstrip("\n"))
            logger.info(f"tippecanoe: {line.rstrip()}")

        proc.wait()                                             

        if proc.returncode != 0:
            raise RuntimeError(f"Tippecanoe failed for res {res}:\n" + "\n".join(out_lines))

        mbtiles_files.append(tmp_mbtiles)                      
        logger.info(f"Done with resolution {res} in {time.time() - start_time:.2f}s")


    # Merge all resolutions into one PMTiles file
    if not mbtiles_files:
        raise RuntimeError("No mbtiles files generated")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)   

    logger.info("Merging resolutions with tile-join...")
    merge_cmd = ["tile-join", "-o", output_path, "--force", *mbtiles_files]

    proc = subprocess.Popen(merge_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    out_lines = []
    for line in proc.stdout:
        out_lines.append(line.rstrip("\n"))
        logger.info(f"tile-join: {line.rstrip()}")

    proc.wait()                                                

    if proc.returncode != 0:
        raise RuntimeError("tile-join failed:\n" + "\n".join(out_lines))

    logger.info("✅ FINISHED merging resolutions")
    logger.info(f"Total time: {time.time() - start_time:.2f}s → {output_path}")
    
    # Cleanup temp files
    for tmp_mbtiles in mbtiles_files:
        os.remove(tmp_mbtiles)
        logger.info(f"Removed temp file: {tmp_mbtiles}")