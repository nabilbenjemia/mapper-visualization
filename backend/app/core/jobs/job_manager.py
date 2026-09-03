import uuid
from datetime import datetime, timezone
from config.job_status import JobStatus

jobs = {}


def create_job(dataset: str, category=None, mode=None):
    jobs_to_delete = []

    for job_id, job in jobs.items():
        if (
            job["dataset"] == dataset
            and job["category"] == category
            and job["mode"] == mode
        ):
            jobs_to_delete.append(job_id)

    for job_id in jobs_to_delete:
        del jobs[job_id]
        
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "dataset": dataset,
        "category": category,
        "mode": mode,
        "status": JobStatus.PROCESSING,
        "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "finished_at": None,
    }

    return job_id


def get_job(job_id: str):
    return jobs.get(job_id)

def list_jobs():
    return list(jobs.values())


def update_job(job_id: str, status: str, error=None):
    job = jobs.get(job_id)

    if job:
        job["status"] = status
        job["error"] = error

        if status in (JobStatus.SUCCESS, JobStatus.ERROR):
            job["finished_at"] = datetime.now(timezone.utc).isoformat()