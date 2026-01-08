import sys

# Disable telemetry completely
try:
    import chromadb
    if hasattr(chromadb, "telemetry"):
        chromadb.telemetry.capture = lambda *args, **kwargs: None
except Exception as e:
    print(f"Telemetry patch failed: {e}")
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

from dotenv import load_dotenv
from pdf_processor import PDFProcessor
from vector_store_manager import VectorStoreManager
from memory_manager import MemoryManager
from chatbot import LAMAChatbot
from langchain.agents import AgentExecutor, create_openai_functions_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Your frontend ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components once
load_dotenv()
PDF_PATH = "Lama.pdf"

vector_manager = VectorStoreManager()
if not vector_manager.vector_store_exists():
    print("Creating vector store...")
    processor = PDFProcessor()
    chunks = processor.process_pdf(PDF_PATH)
    vector_manager.create_vector_store(chunks)

vector_store = vector_manager.load_vector_store()
memory_manager = MemoryManager()
chatbot = LAMAChatbot(vector_store, memory_manager)

# Initialize an agent executor (same behavior as main.py) so the web API can use it
try:
    agent = create_openai_functions_agent(chatbot.llm, [chatbot.retriever_tool], prompt=chatbot.prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=[chatbot.retriever_tool],
        memory=memory_manager.get_memory(),
        verbose=True,
    )
    chatbot.set_agent_executor(executor)
    print("Agent executor initialized for web API.")
except Exception as e:
    print(f"Failed to initialize agent executor: {e}")


@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    if not message:
        return {"error": "Empty message"}
    print(f"Customer: {message}")
    response = chatbot.ask(message)
    return {"response": response}