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

#FILE_PATH = "/mnt/data/h3_geojson/hamburg_fuel_station_drive.geojson" 
FILE_PATH = "/mnt/data/h3_geojson/full.geojson"
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

'''
def convert_to_geojson(df, limit=5):
    features = []
    df = df[["h3", "poi_ambulance_station_walk"]].head(limit) 
    
    print("Input data:")
    print(df)

    for _, row in df.iterrows():
        h3_index = row["h3"]
        #value = row["value"]

        # get hexagon boundary
        boundary = h3.cell_to_boundary(h3_index) # returns list of (lat, lng) tuples !!!!!!! 
        
        # flip (lat, lng) -> (lng, lat)
        boundary = [(lng, lat) for lat, lng in boundary]

        lat, lng = h3.cell_to_latlng(h3_index) # get center point (lat, lng)
        
        polygon = Polygon(boundary)
        
        properties = row.drop("h3").to_dict() #take all columns except "h3" as properties
        properties["lat"] = lat
        properties["lng"] = lng

        features.append({
            "type": "Feature",
            "geometry": mapping(polygon),
            "properties": properties
        })

    return {
        "features": features
    }
'''

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
                
@app.on_event("startup")
def load_data():
    global geojson_data
    city = "hamburg"
    
    """
    if True:  # os.path.exists(FILE_PATH):
        load_geojson_dir()
        print("GeoJSON files loaded:", list(GEOJSON_CACHE.keys()))
    else:
    
        print("Generating GeoJSON from parquet...")
        start_time = time.time()
        df = pd.read_parquet("/mnt/data/results/2026-02-19T14-11-24Z_germany-hamburg_ee98d3/cells.parquet")

        modes = [
        "walk",
        "bike",
        "drive",
        "transit",
        "transit_bus",
        "transit_rail",
        "walk_transit",
        #"walk_transit_bus",
        #"walk_transit_rail"
        ]
        
        for mode in modes:
            geojson_data = convert_to_geojson(df, mode=mode)

            mode_file_path = f"/mnt/data/h3_geojson/{city}/{mode}.geojson"
            os.makedirs(os.path.dirname(mode_file_path), exist_ok=True)
            print("Saving GeoJSON to file: ", mode_file_path)
            with open(mode_file_path, "w") as f:
                json.dump(geojson_data, f)
            
            end_time = time.time()
            elapsed = end_time - start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = elapsed % 60

            print(f"GeoJSON {mode} for {city} generated and saved in {f'{hours}h ' if hours else ''} {minutes}m {seconds:.2f}s 🚀")
"""
    #print("first feature's H3 index:", geojson_data["features"][0]["properties"]["h3"])
    #print("first feature's geometry:", geojson_data["features"][0]["geometry"])
    #print("first feature's properties:", geojson_data["features"][0]["properties"])
    #print("first feature's centroid:", (geojson_data["features"][0]["properties"]["lng"], geojson_data["features"][0]["properties"]["lat"]))
    print("Ready!")

@app.get("/geojson/{mode}")
def get_geojson(mode: str):
    data = GEOJSON_CACHE.get(mode)

    if not data:
        return {"error": "mode not found"}

    return data
'''
@app.get("/geojson")
def get_geojson():
    print("Total features in GeoJSON:", len(geojson_data["features"]))
    return {
        "type": "FeatureCollection",
        "features": geojson_data["features"] #[:2000] #20000
    }

   
@app.get("/properties")
def get_properties():
    return {"properties": list(geojson_data["features"][0]["properties"].keys())}

@app.get("/properties/{property_name_suffix}")
def get_property(property_name_suffix: str):
    matches = [
        p for p in geojson_data["features"][0]["properties"].keys()
        if p.endswith(property_name_suffix)
    ]
    return {"matches": matches}

app.mount("/data/h3_geojson/", StaticFiles(directory="/mnt/data/h3_geojson/"), name="data")
'''

@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is healthy!"}

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
    
@app.post("/build-tiles/{category}/{mode}")
def build_tiles(category: str, mode: str, background_tasks: BackgroundTasks):
    city = "hamburg"
    parquet_path = "/mnt/data/results/2026-02-19T14-11-24Z_germany-hamburg_ee98d3/cells.parquet"
    output_path = f"/mnt/data/tiles/{city}_{category}_{mode}.pmtiles"

    try:
        background_tasks.add_task(build_pmtiles, parquet_path, output_path, category, mode)
        return {"status": "accepted", "message": f"PMTiles build started for {category} {mode}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    
app.mount(
    "/tiles",
    StaticFiles(directory="/mnt/data/tiles"),
    name="tiles"
)