# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.graph import create_support_graph
from database.db import init_database
from services.vector_store import init_vector_store
import uvicorn
import traceback
from utils.memory import LLMCustomerSupportMemory

app = FastAPI(title="Customer Support API")

# Global dictionary to store user memories
user_memories = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable for the graph
support_graph = None

# Initialize database and vector store on startup
@app.on_event("startup")
async def startup_event():
    global support_graph
    try:
        print("📄 Initializing database...")
        init_database()
        print("✅ Database initialized")
        
        print("📄 Initializing vector store...")
        init_vector_store()
        print("✅ Vector store initialized")
        
        print("📄 Creating support graph...")
        support_graph = create_support_graph()
        print("✅ Support graph created")
        
    except Exception as e:
        print(f"\n❌ ERROR DURING STARTUP:")
        print("="*50)
        traceback.print_exc()
        print("="*50)
        print("\n⚠️ Server is running but support graph failed to initialize!")
        print("Check the error above and fix the issue.\n")

class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        if support_graph is None:
            raise HTTPException(
                status_code=503, 
                detail="Support system not initialized. Check server logs for errors."
            )
        
        # Create or retrieve memory for this user
        if request.user_id not in user_memories:
            user_memories[request.user_id] = LLMCustomerSupportMemory()
        
        # Invoke graph with memory
        result = support_graph.invoke({
            "user_id": request.user_id,
            "message": request.message,
            "response": "",
            "classification": "",
            "sub_classification": "",
            "context": "",
            "memory": user_memories[request.user_id]
        })
        
        return ChatResponse(response=result["response"])
        
    except HTTPException:
        raise
    except Exception as e:
        print("\n" + "="*50)
        print("❌ ERROR in /chat endpoint:")
        print("="*50)
        traceback.print_exc()
        print("="*50 + "\n")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "graph_initialized": support_graph is not None
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)