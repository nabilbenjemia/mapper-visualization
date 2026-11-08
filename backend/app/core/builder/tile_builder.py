import subprocess
import json
import os
import time
import csv
from core.pipeline.parquet_loader import load_layer
from core.pipeline.features import build_feature
from utils.logger import get_logger


def build_pmtiles(dataset: str, parquet_paths: dict, output_path: str, category: str, mode: str):
    logger = get_logger(__name__, dataset)
    logger.info(f"Starting PMTiles build for dataset={dataset}, category={category}, mode={mode}")
    
    start_time = time.time()
    csv_result_path = os.path.dirname(output_path) + "/results.csv"
    logger.info(f"Building PMTiles for category={category}, mode={mode}")

    if not parquet_paths:
        raise RuntimeError("No parquet files provided")
    
    resolutions = sorted(parquet_paths.keys())
    
    if len(resolutions) != 3:
        raise RuntimeError(
            f"Expected 3 resolutions, got {len(resolutions)}: {resolutions}"
        )
    
    logger.info(f"Generated resolutions: {resolutions}")

    tmp_files = []
    mbtiles_files = []
    
    if not os.path.exists(csv_result_path):
        os.makedirs(os.path.dirname(csv_result_path), exist_ok=True)
        with open(csv_result_path, "w", newline="") as f:
            f.write("category,mode,time_seconds,size_mb,status,error_message\n")
    
    try:

        for index, res in enumerate(resolutions):
            parquet_path = parquet_paths[res]
            
            logger.info(f"Processing resolution {res} with parquet {parquet_path}")
            rows = load_layer(dataset, parquet_path)

            tmp_dir = "/mnt/data/tmp"
            os.makedirs(tmp_dir, exist_ok=True)

            tmp_file = os.path.join(
                tmp_dir,
                f"{category}_{mode}_res{res}.geojsonl"
            )

            tmp_mbtiles = os.path.join(
                tmp_dir,
                f"{category}_{mode}_res{res}.mbtiles"
            )
            
            tmp_files.append(tmp_file)

            count = 0
            invalid = 0

            with open(tmp_file, "w") as f:                          
                for h3_index, value in rows:
                    try:
                        feature = build_feature(dataset, h3_index, value)
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

            # Assign zoom ranges based on resolution order
            if index == 0:
                # Lowest resolution → low zooms
                zmin = 0
                zmax = 6

            elif index == 1:
                # Middle resolution → medium zooms
                zmin = 7
                zmax = 9

            else:
                # Highest resolution → high zooms
                zmin = 10
                zmax = 14

            # Only apply densest dropping to the highest resolution
            extra_flags = (
                ["--drop-densest-as-needed"]
                if index == len(resolutions) - 1
                else []
            )

            logger.info(
                f"Resolution {res} → zoom {zmin}-{zmax}"
            )

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