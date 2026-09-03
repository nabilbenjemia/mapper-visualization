from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from core.admin.dataset_service import (
    list_datasets,
    build_all_tiles as service_build_all_tiles,
    build_single_tile as service_build_single_tile,
)
from core.jobs.job_manager import create_job, get_job, list_jobs
from fastapi import HTTPException

app = FastAPI()

# allow frontend to call backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/tiles",
    StaticFiles(directory="/mnt/data/tiles"),
    name="tiles"
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