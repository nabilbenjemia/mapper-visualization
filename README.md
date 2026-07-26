## Run backend
1) source venv/bin/activate
2) cd backend/app
3) uvicorn main:app --reload &

N:B: & puts it in backgound. To check running processes run ´jobs´. To make it in forground e.g fg %1

## Run frontend
1) cd frontend
2) npm run dev


## Run independently 
tmux new -s tiles
curl -X POST http://localhost:8000/build-tiles/germany/2026-06-30T05-14-58Z_europe-germany_e046f3
Ctrl+B D

Reconnect later: tmux attach -t tiles


## Tiles location
/mnt/data
    |----tiles
            |-----germany
                    |------2026-03-18T14-34-36Z_europe-germany_b9dada
                    |------2026-06-30T05-14-58Z_europe-germany_e046f3

## Check if a column exists in parquet
python3 -c "import pyarrow.parquet as pq; print([c for c in pq.read_schema('/mnt/data/results/2026-06-30T05-14-58Z_europe-germany_e046f3/cells_res10.parquet').names if 'poi_embassy_' in c.lower()])"