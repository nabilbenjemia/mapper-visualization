from pathlib import Path
import json
import os
from core.builder.tile_builder import build_pmtiles
from core.builder.frontend_metadata import export_frontend_metadata
from scripts.aggregate_h3 import create_category_mode_resolutions
from core.jobs.job_manager import create_job, update_job
from config.job_status import JobStatus


RESULTS_DIR = Path("/mnt/data/results")
TILES_DIR = Path("/mnt/data/tiles")


def build_single_tile(dataset: str, category: str, mode: str, background_tasks):

    dataset_path = RESULTS_DIR / dataset

    if not dataset_path.is_dir():
        return {
            "status": "error",
            "message": f"Dataset '{dataset}' not found."
        }
    
    input_parquet = dataset_path / "cells.parquet"

    if not valid_parquet(input_parquet):
        return {
            "status": "error",
            "message": f"Source parquet '{input_parquet}' not found or is empty."
        }
    
    manifest_path = dataset_path / "run_manifest.json"

    if not manifest_path.exists():
        return {
            "status": "error",
            "message": f"Manifest file for dataset '{dataset}' not found."
        }

    with open(manifest_path) as f:
        manifest = json.load(f)

    region = manifest.get("meta", {}).get("region", "").split("/")[-1]
    base_resolution = manifest.get("meta", {}).get("h3_res")

    if base_resolution is None:
        return {
            "status": "error",
            "message": f"Base H3 resolution not found in manifest for dataset '{dataset}'."
        }
    
    if not region:
        return {
            "status": "error",
            "message": f"Region name could not be determined."
        }

    job_id = create_job(
        dataset=dataset,
        category=category,
        mode=mode
    )

    background_tasks.add_task(
        generate_single_tile,
        dataset,
        region,
        category,
        mode,
        base_resolution,
        job_id
    )


    return {
        "job_id": job_id,
        "status": JobStatus.PROCESSING,
        "dataset": dataset,
        "region": region,
        "category": category,
        "mode": mode
    }
    
    
def build_all_tiles(dataset: str, background_tasks):

    try:
        dataset_path = RESULTS_DIR / dataset

        if not dataset_path.is_dir():
            return {
                "status": "error",
                "message": f"Dataset '{dataset}' not found."
            }

        manifest_path = dataset_path / "run_manifest.json"

        if not manifest_path.exists():
            return {
                "status": "error",
                "message": f"Manifest file for dataset '{dataset}' not found."
            }

        with open(manifest_path) as f:
            manifest = json.load(f)

        region = manifest.get("meta", {}).get("region", "").split("/")[-1]
        categories = manifest.get("meta", {}).get("amenities", [])
        modes = manifest.get("meta", {}).get("modes", [])
        base_resolution = manifest.get("meta", {}).get("h3_res")

        if base_resolution is None:
            return {
                "status": "error",
                "message": f"Base H3 resolution not found in manifest for dataset '{dataset}'."
            }

        if not region:
            return {
                "status": "error",
                "message": f"Region name could not be determined."
            }

        job_id = create_job(
            dataset=dataset
        )

        background_tasks.add_task(
            generate_all_tiles,
            dataset,
            region,
            categories,
            modes,
            base_resolution,
            job_id
        )


        return {
            "job_id": job_id,
            "status": JobStatus.PROCESSING,
            "dataset": dataset,
            "region": region
        }


    except RuntimeError as e:
        return {
            "status": "error",
            "message": str(e)
        }



def generate_single_tile(dataset: str, region: str, category: str, mode: str, base_resolution: int, job_id: str):
    temp_parquets = {}
    
    try: 
        dataset_path = RESULTS_DIR / dataset

        prepare_dataset(dataset, region)

        input_parquet = dataset_path / "cells.parquet"
        
        temp_parquets = create_category_mode_resolutions(
            dataset=dataset,
            input_parquet=str(input_parquet),
            category=category,
            mode=mode,
            input_resolution=base_resolution,
            resolutions=[
                base_resolution - 4,
                base_resolution - 2,
                base_resolution,
            ],
        )

        output_path = (
            TILES_DIR
            / region
            / dataset
            / f"{region}_{category}_{mode}.pmtiles"
        )


        build_pmtiles(
            dataset,
            temp_parquets,
            output_path,
            category,
            mode,
        )
        
        update_job(job_id, status=JobStatus.SUCCESS)
        
        return True
        
    except Exception as e:
        update_job(job_id, status=JobStatus.ERROR, error=str(e))
        return False
    
    finally:
        for path in temp_parquets.values():
            if path and os.path.exists(path):
                os.remove(path)
    
    
def generate_all_tiles(dataset: str, region: str, categories: list, modes: list, base_resolution: int, parent_job_id: str):
    has_error = False
    for category in categories:
        for mode in modes:
            output_path = (
                TILES_DIR
                / region
                / dataset
                / f"{region}_{category}_{mode}.pmtiles"
            )

            if output_path.exists():
                continue

            child_job_id  = create_job(
                dataset=dataset,
                category=category,
                mode=mode
            )

            success = generate_single_tile(
                dataset=dataset,
                region=region,
                category=category,
                mode=mode,
                base_resolution=base_resolution,
                job_id=child_job_id
            )
            
            if not success:
                has_error = True
            
    if has_error:
        update_job(
            parent_job_id,
            status=JobStatus.ERROR
        )
    else:
        update_job(
            parent_job_id,
            status=JobStatus.SUCCESS
        )

def prepare_dataset(dataset: str, region: str):
    dataset_path = RESULTS_DIR / dataset
    
    #create_resolution_parquets(dataset)

    export_frontend_metadata(
        dataset_path / "run_manifest.json",
        TILES_DIR / region / dataset
    )
    
def get_dataset_status(dataset_path: Path, dataset: str):

    manifest_path = dataset_path / "run_manifest.json"

    if not manifest_path.exists():
        return {
            "region": None,
            "pmtiles": {
                "available": 0,
                "expected": 0,
                "status": "missing_manifest"
            },
            "categories": []
        }

    with open(manifest_path) as f:
        manifest = json.load(f)

    region = manifest.get("meta", {}).get("region", "").split("/")[-1]

    categories = manifest.get("meta", {}).get("amenities", [])
    modes = manifest.get("meta", {}).get("modes", [])

    tiles_path = TILES_DIR / region / dataset

    available_tiles = set()

    if tiles_path.exists():
        available_tiles = {
            path.name
            for path in tiles_path.glob("*.pmtiles")
        }

    category_status = []

    for category in categories:

        mode_status = []

        for mode in modes:

            filename = f"{region}_{category}_{mode}.pmtiles"

            mode_status.append({
                "mode": mode,
                "available": filename in available_tiles
            })

        category_status.append({
            "category": category,
            "modes": mode_status
        })

    expected = len(categories) * len(modes)
    available = sum(
        combination["available"]
        for category in category_status
        for combination in category["modes"]
    )

    if available == 0:
        status = "none"
    elif available < expected:
        status = "partial"
    else:
        status = "complete"

    return {
        "region": region,
        "pmtiles": {
            "available": available,
            "expected": expected,
            "status": status
        },
        "categories": category_status
    }
    
    
def list_datasets():

    datasets = []

    for dataset_path in RESULTS_DIR.iterdir():

        if not dataset_path.is_dir():
            continue

        dataset = dataset_path.name

        if not any(dataset_path.glob("*.parquet")):
            continue

        info = get_dataset_status(
            dataset_path,
            dataset
        )

        datasets.append({
            "dataset": dataset,
            "source_available": True,
            **info
        })

    return datasets

def valid_parquet(path):
    return os.path.exists(path) and os.path.getsize(path) > 0