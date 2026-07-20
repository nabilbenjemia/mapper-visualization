import subprocess
import json
import os
import time
import csv
from core.pipeline.parquet_loader import load_layer
from core.pipeline.features import build_feature
from utils.logger import get_logger

logger = get_logger(__name__)

def build_pmtiles(parquet_paths: dict, output_path: str, category: str, mode: str):
    start_time = time.time()
    csv_result_path = os.path.dirname(output_path) + "/results.csv"
    logger.info(f"Building PMTiles for category={category}, mode={mode}")

    zoom_config = {
        6:  {"min_zoom": 0,  "max_zoom": 6},
        8:  {"min_zoom": 7,  "max_zoom": 9},
        10: {"min_zoom": 10, "max_zoom": 14},
    }

    tmp_files = []
    mbtiles_files = []
    
    if not os.path.exists(csv_result_path):
        os.makedirs(os.path.dirname(csv_result_path), exist_ok=True)
        with open(csv_result_path, "w", newline="") as f:
            f.write("category,mode,time_seconds,size_mb,status,error_message\n")
    
    try:

        for res, parquet_path in parquet_paths.items():
            logger.info(f"Processing resolution {res} with parquet {parquet_path}")
            rows = load_layer(parquet_path, category, mode)

            tmp_file = f"/mnt/data/tmp/{category}_{mode}_res{res}.geojsonl"
            tmp_mbtiles = f"/mnt/data/tmp/{category}_{mode}_res{res}.mbtiles"
            
            tmp_files.append(tmp_file)

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

        total_time = time.time() - start_time
        
        size_mb = round(os.path.getsize(output_path) / (1024 * 1024), 2)
        
        logger.info("✅ FINISHED merging resolutions")
        logger.info(f"Total time: {total_time:.2f}s → {output_path}")
        
        with open(csv_result_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                category, 
                mode, 
                f"{total_time:.2f}", 
                size_mb,
                "success",
                ""
            ])

    except RuntimeError as e:
        logger.error(f"Error building PMTiles: {e}")
        total_time = time.time() - start_time

        with open(csv_result_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                category, 
                mode, 
                f"{total_time:.2f}", 
                "",
                "failed",
                str(e).split("\n")[0]
            ])
            
        raise 
    
    finally:
        # Cleanup temp files
        for tmp_file in tmp_files:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
                logger.info(f"Removed temp file: {tmp_file}")

        for tmp_mbtiles in mbtiles_files:
            if os.path.exists(tmp_mbtiles):
                os.remove(tmp_mbtiles)
                logger.info(f"Removed temp file: {tmp_mbtiles}")