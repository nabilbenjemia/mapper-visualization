<p align="center">
  <img src="./assets/mapper_logo.png" alt="Mapper logo" width="500" />
</p>

# Mapper Frontend

A full-stack geospatial tile viewer and dataset pipeline for exploring aggregated H3/parquet-based map data. The project includes:

- A FastAPI backend that exposes dataset metadata and tile-generation jobs
- A public frontend map UI built with Vue and MapLibre
- An admin frontend for dataset management and tile generation
- A data processing pipeline that converts parquet result files into PMTiles for fast map rendering

## Project structure

- `backend/` — FastAPI service and tile-building pipeline
- `frontend/` — main user-facing map application
- `admin-frontend/` — admin dashboard for dataset/tile management
- `docker-compose.yml` — local multi-service orchestration
- `/mnt/data/results` — generated dataset inputs
- `/mnt/data/tiles` — generated PMTiles output

## What this app does

The backend reads dataset folders under `/mnt/data/results`, looks for metadata such as run manifests and parquet files, and produces tiled vector/raster map outputs for specific region/category/mode combinations. Those tiles are served under `/tiles` and consumed by the frontend map viewer.

The frontend then renders map layers using MapLibre with data produced from these generated tile bundles. The admin interface can trigger datasets to be built and monitor background job status.

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Access to the shared data directories:
  - `/mnt/data/results`
  - `/mnt/data/tiles`

## Local development

### 1) Backend

From the repo root:

```bash
source venv/bin/activate
cd backend/app
uvicorn main:app --reload
```

The API runs on:

- http://localhost:8000

Useful endpoints:

- `GET /health`
- `GET /datasets`
- `GET /admin/datasets`
- `POST /admin/datasets/{dataset}/build`
- `POST /admin/datasets/{dataset}/build/{category}/{mode}`
- `GET /admin/jobs`
- `GET /admin/jobs/{job_id}`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI is typically available at:

- http://localhost:5173

### 3) Admin frontend

```bash
cd admin-frontend
npm install
npm run dev
```

The admin dashboard is typically available at:

- http://localhost:5174

## Docker-based startup

This project also includes a Docker Compose setup for running services together:

```bash
docker compose up --build
```

Service layout:

- Backend: http://localhost:8000
- Frontend: http://localhost:80
- Admin frontend: http://localhost:3000

## Background tile generation

Some datasets are built asynchronously. The project includes a job manager and background processing pattern for long-running tile-generation tasks.

Example of running a one-off generation in a detached tmux session:

```bash
tmux new -s tiles
curl -X POST http://localhost:8000/admin/datasets/germany/build
Ctrl+B D
```

Reconnect later with:

```bash
tmux attach -t tiles
```

Generated tiles live under:

```text
/mnt/data
└── tiles
    └── germany
        └── <dataset-name>
            ├── germany_amenity_mode.pmtiles
            └── ...
```

## Data layout

The expected data inputs are organized like this:

```text
/mnt/data
├── results
│   └── <dataset_name>
│       ├── cells.parquet
│       ├── run_manifest.json
│       └── ...
└── tiles
    └── <region>
        └── <dataset_name>
            └── <generated_tile_files>
```

## Useful checks

Check whether a parquet column exists:

```bash
python3 -c "import pyarrow.parquet as pq; print([c for c in pq.read_schema('/mnt/data/results/<dataset_name>/cells.parquet').names if 'poi_alcohol_shop_walk' in c.lower()])"
```

Check if the backend is healthy:

```bash
curl http://localhost:8000/health
```

## Notes

- The backend expects datasets to already exist in `/mnt/data/results`.
- Tile generation can take time; monitor jobs through the admin endpoints.
- The root README is intentionally focused on setup and operating the project rather than implementation details.
