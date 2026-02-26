# run.py
import uvicorn

if __name__ == "__main__":
    # print("Starting Customer Support API...")
    # print("API will be available at http://localhost:8000")
    # print("Docs available at http://localhost:8000/docs")
    # print("="*50)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)