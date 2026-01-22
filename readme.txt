Run order: start FastAPI (agent1) on 8000, Flask (agent2) on 5000, Node router on 8001, then Vite dev on 3000.
agent 1 : uvicorn app:app --reload --port 8000
agent 2 :  python app.py  
backend : node server.js 
frontend : npm run dev
