# README.md

# Production-Ready Customer Support Backend

AI-powered customer support system using LangGraph, OpenRouter LLMs, and PDF knowledge base.

## Features

- ✅ Query classification (greeting/irrelevant/relevant)
- ✅ Company info from PDF (lama1.pdf) via RAG
- ✅ Order queries from SQL database
- ✅ Conversation memory
- ✅ OpenRouter LLM integration
- ✅ FAISS vector store
- ✅ Production-ready FastAPI backend

## Setup

1. Install dependencies:
```bash
chmod +x setup.sh
./setup.sh
```

2. Configure environment:
   - Copy `.env.example` to `.env`
   - Add your OpenRouter API key
   - Set your preferred model (default: llama-3.1-8b-instruct:free)

3. Add your PDF:
   - Place `lama1.pdf` in the project root
   - Or update `PDF_PATH` in `.env`

4. Run the application:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python run.py
```

## API Usage

### Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "What does the PDF say about your services?"
  }'
```

Response:
```json
{
  "response": "Based on the document, our services include..."
}
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Testing Examples

### Greeting
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "Hello!"}'
```

### Company Info (from PDF)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "What are your policies?"}'
```

### Order Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "Show me my orders"}'
```

### Irrelevant Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "What is the weather today?"}'
```

## Architecture
```
User Query
    ↓
[Classify: greeting/irrelevant/relevant]
    ↓
If relevant → [Sub-classify: company_info/order_related]
    ↓
company_info → Check Memory → PDF Vector Search → Response
order_related → SQL Database → Response
```

## Tech Stack

- **FastAPI**: REST API
- **LangGraph**: State machine routing
- **LangChain**: LLM orchestration
- **OpenRouter**: LLM provider
- **FAISS**: Vector database
- **SQLite**: Order database
- **PyPDF**: PDF processing

## File Structure
```
.
├── app.py              # FastAPI application
├── graph.py            # LangGraph workflow
├── llm.py              # OpenRouter LLM setup
├── classifiers.py      # Query classifiers
├── memory.py           # Conversation memory
├── vector_store.py     # PDF vector store
├── db.py               # SQL database
├── run.py              # Application runner
├── requirements.txt    # Dependencies
├── .env.example        # Environment template
└── lama1.pdf          # Your knowledge base
```

## OpenRouter Models

Update `MODEL_NAME` in `.env` to use different models:
- `meta-llama/llama-3.1-8b-instruct:free`
- `meta-llama/llama-3.1-70b-instruct`
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4-turbo`

## Production Considerations

- Add authentication middleware
- Implement rate limiting
- Add logging and monitoring
- Use persistent conversation storage
- Scale with Redis for memory
- Deploy with Docker/Kubernetes