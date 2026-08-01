from pathlib import Path
import json

from config.categories import Category
from config.modes import Mode
from core.builder.tile_builder import build_pmtiles
from core.builder.frontend_metadata import export_frontend_metadata
from scripts.aggregate_h3 import create_resolution_parquets


RESULTS_DIR = Path("/mnt/data/results")
TILES_DIR = Path("/mnt/data/tiles")


def build_single_tile(dataset: str, category: str, mode: str, background_tasks):

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


    background_tasks.add_task(
        generate_single_tile,
        dataset,
        region,
        category,
        mode
    )


    return {
        "status": "queued",
        "dataset": dataset,
        "region": region,
        "category": category,
        "mode": mode
    }
    
    
def build_dataset_tiles(dataset: str, background_tasks):

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

        if not region:
            return {
                "status": "error",
                "message": f"Region name could not be determined."
            }


        background_tasks.add_task(
            generate_all_tiles,
            dataset,
            region,
            categories,
            modes
        )


        return {
            "status": "queued",
            "dataset": dataset
        }


    except RuntimeError as e:
        return {
            "status": "error",
            "message": str(e)
        }


def generate_single_tile(dataset: str, region: str, category: str, mode: str):

    #Add job updates and try/except for error handling and logging
    dataset_path = RESULTS_DIR / dataset

    prepare_dataset(dataset, region)

    output_path = (
        TILES_DIR
        / region
        / dataset
        / f"{region}_{category}_{mode}.pmtiles"
    )


    build_pmtiles(
        {
            6: dataset_path / "cells_res6.parquet",
            8: dataset_path / "cells_res8.parquet",
            10: dataset_path / "cells_res10.parquet"
        },
        output_path,
        category,
        mode
    )
    
    
def generate_all_tiles(dataset: str, region: str, categories: list, modes: list):

    dataset_path = RESULTS_DIR / dataset

    prepare_dataset(dataset, region)
    
    manifest_path = dataset_path / "run_manifest.json"

    if not manifest_path.exists():
        return {
            "region": None,
            "pmtiles": {
                "available": 0,
                "expected": 0,
                "status": "missing_manifest"
            }
        }

    with open(manifest_path) as f:
        manifest = json.load(f)

    region = manifest.get("meta", {}).get("region", "").split("/")[-1]

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

            build_pmtiles(
                {
                    6: dataset_path / "cells_res6.parquet",
                    8: dataset_path / "cells_res8.parquet",
                    10: dataset_path / "cells_res10.parquet"
                },
                output_path,
                category,
                mode
            )
            

def prepare_dataset(dataset: str, region: str):
    dataset_path = RESULTS_DIR / dataset
    
    create_resolution_parquets(dataset)

    export_frontend_metadata(
        dataset_path / "run_manifest.json",
        TILES_DIR / region / dataset
    )
    
def get_pmtiles_status(dataset_path: Path, dataset: str):

    manifest_path = dataset_path / "run_manifest.json"

    if not manifest_path.exists():
        return {
            "region": None,
            "pmtiles": {
                "available": 0,
                "expected": 0,
                "status": "missing_manifest"
            }
        }

    with open(manifest_path) as f:
        manifest = json.load(f)

    region = manifest.get("meta", {}).get("region", "").split("/")[-1]

    categories = (
        manifest
        .get("meta", {})
        .get("amenities", [])
    )

    modes = (
        manifest
        .get("meta", {})
        .get("modes", [])
    )


    expected = len(categories) * len(modes)


    tiles_path = (
        TILES_DIR
        / region
        / dataset
    )


    available = 0

    if tiles_path.exists():
        available = len(
            list(tiles_path.glob("*.pmtiles"))
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
        }
    }
    
    
def list_datasets():

    datasets = []

    for dataset_path in RESULTS_DIR.iterdir():

        if not dataset_path.is_dir():
            continue

        dataset = dataset_path.name

        if not (
            (dataset_path / "cells.parquet").exists()
            or
            (dataset_path / "cells_res10.parquet").exists()
        ):
            continue


        info = get_pmtiles_status(
            dataset_path,
            dataset
        )

        datasets.append({
            "dataset": dataset,
            "source_available": True,
            **info
        })

    return datasets