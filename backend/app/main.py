from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.admin.dataset_service import (
    list_datasets,
    list_available_datasets,
    build_all_tiles as service_build_all_tiles,
    build_single_tile as service_build_single_tile,
)
from core.jobs.job_manager import create_job, get_job, list_jobs, update_job
import os


app = FastAPI()

FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost",
    "http://127.0.0.1",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Accept-Ranges",
        "Content-Length",
        "Content-Range",
        "Content-Type",
        "ETag",
        "Last-Modified",
    ],
)

TILES_DIRECTORY = "/mnt/data/tiles"

if not os.path.isdir(TILES_DIRECTORY):
    raise RuntimeError(f"Tiles directory does not exist: {TILES_DIRECTORY}")

app.mount(
    "/tiles",
    StaticFiles(directory=TILES_DIRECTORY),
    name="tiles",
)

@app.on_event("startup")
def load_data():
    print("Ready!")

@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is healthy!"}
    
@app.get("/admin/datasets")
def get_datasets():
    return list_datasets()

@app.get("/datasets")
def get_available_datasets():
    return list_available_datasets()

@app.post("/admin/datasets/{dataset}/build")
def build_all_tiles(dataset: str, background_tasks: BackgroundTasks):
    return service_build_all_tiles(dataset, background_tasks)
    
@app.post("/admin/datasets/{dataset}/build/{category}/{mode}")
def build_tiles(dataset: str, category: str, mode: str, background_tasks: BackgroundTasks):
    return service_build_single_tile(dataset, category, mode, background_tasks)

@app.get("/admin/jobs/{job_id}")
def get_job_status(job_id: str):
    job = get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' not found."
        )

    return job

@app.get("/admin/jobs")
def get_all_jobs():
    return list_jobs()