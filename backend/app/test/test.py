import pandas as pd
import h3
import json
import os
import time
from shapely.geometry import Polygon, mapping
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config.layers import layer_name
from config.categories import Category
from config.modes import Mode
from core.pipeline.parquet_loader import load_layer
from core.pipeline.h3_to_geo import h3_to_geometry
from core.builder.tile_builder import build_pmtiles
from pydantic import BaseModel
from scripts.aggregate_h3 import create_resolution_parquets
from core.builder.frontend_metadata import export_frontend_metadata

BASE_DIR = "/mnt/data/h3_geojson/hamburg"

app = FastAPI()

# allow frontend to call backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

geojson_data = None

def convert_to_geojson(df, limit=5, columns=None, keep_h3=True, mode="drive"):
    features = []

    # filter columns by mode suffix
    if columns:
        selected_cols = columns
    else:
        selected_cols = [col for col in df.columns if col.endswith(f"_{mode}")]

    df = df[["h3"] + selected_cols]

    #print("Selected columns:", selected_cols)
    #print(df.head())

    for _, row in df.iterrows():
        h3_index = row["h3"]

        # boundary (lat, lng) → (lng, lat)
        boundary = h3.cell_to_boundary(h3_index)
        boundary = [(lng, lat) for lat, lng in boundary]

        polygon = Polygon(boundary)

        # centroid
        lat, lng = h3.cell_to_latlng(h3_index)

        # properties
        properties = row.drop("h3").to_dict()

        if keep_h3:
            properties["h3"] = h3_index

        properties["center"] = {"lng": lng, "lat": lat}

        features.append({
            "type": "Feature",
            "geometry": mapping(polygon),
            "properties": properties
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }


GEOJSON_CACHE = {}

def load_geojson_dir():
    for file in os.listdir(BASE_DIR):
        if file.endswith(".geojson"):
            mode = file.replace(".geojson", "")
            path = os.path.join(BASE_DIR, file)

            print(f"Loading {mode} → {path}")

            with open(path) as f:
                GEOJSON_CACHE[mode] = json.load(f)
                

@app.get("/geojson/{mode}")
def get_geojson(mode: str):
    data = GEOJSON_CACHE.get(mode)

    if not data:
        return {"error": "mode not found"}

    return data


@app.get("/layers/{category}/{mode}")
def get_layer(category: Category, mode: Mode):
    layer = layer_name(category.value, mode.value)
    return {"layer": layer}

@app.get("/test-layer/{category}/{mode}")
def test_layer(category: str, mode: str):
    result = load_layer("/mnt/data/results/2026-02-19T14-11-24Z_germany-hamburg_ee98d3/cells.parquet", category, mode)

    # fetch only a few rows for testing
    rows = result.fetchmany(5)

    return {
        "columns": [desc[0] for desc in result.description],
        "rows": rows
    }
    
@app.get("/test-geo/{h3_index}")
def test_geo(h3_index: str):
    polygon, center = h3_to_geometry(h3_index)

    return {
        "h3_index": h3_index,
        "polygon": polygon,
        "center": {"lng": center[0], "lat": center[1]}
    }
    