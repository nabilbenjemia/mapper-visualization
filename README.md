## Run backend
1) source venv/bin/activate
2) cd backend/app
3) uvicorn main:app --reload

## Run frontend
1) cd frontend
2) npm run dev


## Run independently 
tmux new -s tiles
curl -X POST http://localhost:8000/build-tiles/germany
Ctrl+B D

Reconnect later: tmux attach -t tiles

