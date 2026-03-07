# app.py
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from app.services.graph import create_support_graph
from app.models.database import init_database, get_db_service
from app.services.vector_store import init_vector_store
from app.services.memory import LLMCustomerSupportMemory
from app.services.email.poller import EmailPoller
from app.config import Config
import uvicorn
import traceback
import logging
from typing import Optional

# ── Logging setup ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ── LangSmith setup (optional, for observability) ─────────────────────────
if Config.LANGFUSE_ENABLED and Config.LANGFUSE_SECRET_KEY and Config.LANGFUSE_PUBLIC_KEY:
    try:
        from langfuse.callback import CallbackHandler
        langfuse_handler = CallbackHandler(
            secret_key=Config.LANGFUSE_SECRET_KEY,
            public_key=Config.LANGFUSE_PUBLIC_KEY
        )
        logger.info("LangSmith observability enabled")
    except Exception as e:
        logger.warning(f"Could not initialize LangSmith: {e}")
        langfuse_handler = None
else:
    langfuse_handler = None

support_graph  = None
email_poller   = None

# ── Lifespan Context Manager (Replaces on_event) ───────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global support_graph, email_poller
    
    # --- STARTUP ---
    try:
        logger.info("Validating configuration...")
        Config.validate()
        logger.info("✅ Configuration validated")

        logger.info("📄 Initializing database...")
        init_database()
        logger.info("✅ Database initialized")

        logger.info("📄 Initializing vector store...")
        init_vector_store()
        logger.info("✅ Vector store initialized")

        logger.info("📄 Creating support graph...")
        support_graph = create_support_graph()
        logger.info("✅ Support graph created")

        logger.info("📧 Starting email poller...")
        email_poller = EmailPoller(support_graph=support_graph)
        email_poller.start()
        logger.info("✅ Email poller started")
        
        logger.info("🚀 All systems initialized successfully")

    except Exception as e:
        logger.error("❌ ERROR DURING STARTUP:")
        logger.error("=" * 50)
        logger.error(traceback.format_exc())
        logger.error("=" * 50)
        logger.warning("⚠️ Server is running but one or more components failed to initialize!")

    # Yield control back to FastAPI to run the application
    yield 

    # --- SHUTDOWN ---
    if email_poller:
        logger.info("📧 Stopping email poller...")
        email_poller.stop()
        logger.info("✅ Email poller stopped")

# ── App Initialization ─────────────────────────────────────────────────────
app = FastAPI(title="Customer Support API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Rate limiting setup ────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ── API Key authentication ─────────────────────────────────────────────────
def verify_api_key(x_api_key: str = Header(None)) -> str:
    """Verify API key for protected endpoints."""
    if not Config.API_KEY:
        return "public"
    
    if not x_api_key:
        raise HTTPException(
            status_code=403,
            detail="Missing API key. Provide X-API-Key header."
        )
    
    if x_api_key != Config.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}***")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    return x_api_key


class ChatRequest(BaseModel):
    user_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

class HistoryResponse(BaseModel):
    user_id: str
    conversation_history: list
    memory: dict


@app.post("/chat", response_model=ChatResponse)
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE}/minute")
async def chat(
    request: Request,                   # <-- Added for SlowAPI
    payload: ChatRequest,               # <-- Renamed from 'request' to 'payload'
    api_key: str = Depends(verify_api_key)
):
    """
    Chat endpoint for customer support interactions.
    Requires X-API-Key header if API_KEY is configured.
    """
    try:
        if support_graph is None:
            logger.error("Support graph not initialized")
            raise HTTPException(
                status_code=503,
                detail="Support system not initialized. Check server logs for errors."
            )

        logger.info(f"Chat request from user {payload.user_id}")
        
        mysql_service = get_mysql_service()
        memory = LLMCustomerSupportMemory(
            mysql_service=mysql_service,
            user_id=payload.user_id
        )
        memory.load_from_db()

        conversation_history = memory.get_conversation_history()

        result = support_graph.invoke({
            "user_id":              payload.user_id,
            "message":              payload.message,
            "response":             "",
            "classification":       "",
            "sub_classification":   "",
            "context":              "",
            "memory":               memory,
            "conversation_history": conversation_history,
        })

        logger.info(f"Chat response generated for user {payload.user_id}")
        return ChatResponse(response=result["response"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /chat endpoint for user {payload.user_id}:")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/history/{user_id}", response_model=HistoryResponse)
@limiter.limit(f"{Config.RATE_LIMIT_PER_MINUTE * 2}/minute")
async def get_history(request: Request, user_id: str, api_key: str = Depends(verify_api_key)):
    """
    Retrieve conversation history and memory for a user.
    Requires X-API-Key header if API_KEY is configured.
    """
    try:
        logger.info(f"History request for user {user_id}")
        
        mysql_service = get_mysql_service()
        memory = LLMCustomerSupportMemory(
            mysql_service=mysql_service,
            user_id=user_id
        )
        memory.load_from_db()

        return HistoryResponse(
            user_id=user_id,
            conversation_history=memory.get_conversation_history(),
            memory=memory.get_memory()
        )

    except Exception as e:
        logger.error(f"Error retrieving history for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving history: {str(e)}"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status":              "healthy",
        "graph_initialized":   support_graph is not None,
        "email_poller_active": email_poller is not None and not email_poller._stop_event.is_set(),
        "api_key_required":    bool(Config.API_KEY),
        "rate_limiting":       f"{Config.RATE_LIMIT_PER_MINUTE} requests/minute",
        "log_level":           Config.LOG_LEVEL,
    }


if __name__ == "__main__":
    logger.info("Starting Customer Support API server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)