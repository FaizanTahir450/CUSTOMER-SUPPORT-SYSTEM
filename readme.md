# LUMINA - Sustainable Fashion E-Commerce Platform

AI-powered sustainable fashion e-commerce platform with customer support chatbot, built with React, Node.js, Python/FastAPI, and Supabase.

## Architecture Overview

```
┌─────────────────────────┐
│   React Frontend        │
│ (lumina-sustainable-   │
│   fashion)              │
└────────┬────────────────┘
         │ (JWT Bearer Token)
         │
    ┌────┴────────────────────────┐
    │                             │
┌───▼──────────────────┐  ┌──────▼─────────────────┐
│ Node.js Auth Server  │  │ Python AI Backend      │
│ (backend-nodejs)     │  │ (backend-python)       │
│                      │  │                        │
│ • Signup/Login       │  │ • Customer Support Chat│
│ • JWT Generation     │  │ • RAG + LLM            │
│ • Password Reset     │  │ • Conversation Memory  │
└───┬──────────────────┘  └──────┬─────────────────┘
    │                            │
    └────────┬───────────────────┘
             │
        ┌────▼──────────────────┐
        │  Supabase PostgreSQL  │
        │                       │
        │ • Users table         │
        │ • User memory (JSON)  │
        │ • Orders & Products   │
        │ • Admin data          │
        └───────────────────────┘
```

## Features

### Authentication
- ✅ User signup/login with email
- ✅ JWT token-based authentication
- ✅ Role-based access control (user/admin)
- ✅ Password reset flow
- ✅ Secure token storage (localStorage)

### Chat & Customer Support
- ✅ AI-powered customer support chatbot (Sophia)
- ✅ Query classification (greeting/irrelevant/relevant)
- ✅ Company info retrieval via RAG from PDF
- ✅ Order query support from database
- ✅ Conversation memory (LLM-extracted facts only)
- ✅ RAG with FAISS vector store
- ✅ OpenRouter LLM integration

### E-Commerce (In Development)
- 🔄 Product catalog (hardcoded - API pending)
- 🔄 Shopping cart (frontend only)
- 🔄 Orders (database schema ready - endpoints pending)
- 🔄 Admin dashboard (hardcoded - endpoints pending)

## Quick Start

### 1. Setup Node.js Backend (Authentication Server)
```bash
cd backend-nodejs
npm install
```

Create `.env`:
```
SUPABASE_URL=https://ovjcaowxkvjlypqchcuy.supabase.co
SUPABASE_ANON_KEY=<your_key>
JWT_SECRET=your_secret_key_here_change_this_in_production
PORT=4000
```

Run:
```bash
npm run dev
```

### 2. Setup Python Backend (AI Support)
```bash
cd backend-python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```
JWT_SECRET=your_secret_key_here_change_this_in_production
OPENROUTER_API_KEY=<your_openrouter_key>
SUPABASE_URL=https://ovjcaowxkvjlypqchcuy.supabase.co
SUPABASE_ANON_KEY=<your_key>
PDF_PATH=lama1.pdf
```

Run:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Setup React Frontend
```bash
cd lumina-sustainable-fashion
npm install
npm run dev
```

Runs on `http://localhost:3000`

## API Endpoints

### Node.js Backend (Port 4000)

**POST /auth/signup**
```bash
curl -X POST http://localhost:4000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

**POST /auth/login**
```bash
curl -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

Response includes JWT token and user role.

### Python Backend (Port 8000)

**POST /chat** (requires JWT)
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <jwt_token>" \
  -d '{
    "message": "What are your company policies?"
  }'
```

**GET /history** (requires JWT)
```bash
curl -X GET http://localhost:8000/history \
  -H "Authorization: Bearer <jwt_token>"
```

Returns: User's extracted memory facts (not full chat history).

**POST /health**
```bash
curl http://localhost:8000/health
```

## Database Schema

### Users Table
- `user_id` (UUID, PK)
- `email` (string, unique)
- `password` (hashed)
- `role` ('user' or 'admin')
- `memory` (JSON - LLM-extracted facts)
- `created_at`, `updated_at`

### Additional Tables
- `password_reset_tokens` - For password reset flow
- `products` - Product catalog (for future endpoints)
- `orders` - Order history
- `order_items` - Order line items
- Full schema in `backend-python/sql/complete_schema_CORRECTED.sql`

## Chat System

### How It Works
1. User sends message via React frontend
2. Frontend sends message + JWT token to Python backend `/chat`
3. Python backend:
   - Verifies JWT token (extracts user_id)
   - Loads user's stored memory (LLM-extracted facts)
   - Classifies message (greeting/irrelevant/relevant)
   - Routes to appropriate handler:
     - **Greeting** → Simple response
     - **Company Info** → RAG search in PDF
     - **Order Query** → Database lookup
     - **Irrelevant** → Witty decline
   - **Extracts facts** from user message and saves to memory
   - Returns AI response

### Memory & Facts
- **What's stored**: Only LLM-extracted facts (customer name, product type, issue, emotion, urgency)
- **What's NOT stored**: Full conversation history
- **Storage**: `users.memory` JSON column in Supabase
- **Purpose**: Provide context for future conversations

## Configuration

### JWT Secret
**CRITICAL**: Both backends MUST use the same `JWT_SECRET` in `.env`
- Python backend reads JWT_SECRET to verify tokens from Node.js
- If mismatched, you'll get "Signature verification failed" errors

### OpenRouter API Key
Get a free API key at https://openrouter.ai/
- Used for LLM chat responses
- Default model: `meta-llama/llama-3.1-8b-instruct:free`

### Supabase Configuration
1. Create project at https://supabase.com
2. Get `SUPABASE_URL` and `SUPABASE_ANON_KEY`
3. Add to `.env` in both backends
4. Run SQL schema: `backend-python/sql/complete_schema_CORRECTED.sql`

## Tech Stack

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **TypeScript** - Type safety
- **Supabase JS Client** - Database access

### Node.js Backend
- **Express** - REST API
- **TypeScript** - Type safety
- **JWT** - Authentication tokens
- **bcryptjs** - Password hashing
- **Supabase** - Database

### Python Backend
- **FastAPI** - REST API
- **LangGraph** - Workflow routing
- **LangChain** - LLM orchestration
- **OpenRouter** - LLM provider
- **FAISS** - Vector search
- **PyPDF** - PDF processing
- **SQLAlchemy** - Database ORM
- **PyJWT** - Token verification

### Database
- **Supabase** (PostgreSQL) - Unified data layer

## Environment Variables

### backend-nodejs/.env
```
SUPABASE_URL=<postgresql_url>
SUPABASE_ANON_KEY=<anon_key>
JWT_SECRET=<secret_key>
PORT=4000
```

### backend-python/.env
```
JWT_SECRET=<same_as_nodejs>
OPENROUTER_API_KEY=<api_key>
SUPABASE_URL=<postgresql_url>
SUPABASE_ANON_KEY=<anon_key>
PDF_PATH=lama1.pdf
MODEL_NAME=meta-llama/llama-3.1-8b-instruct:free
RATE_LIMIT_PER_MINUTE=60
```

### lumina-sustainable-fashion/.env
```
VITE_API_URL=http://localhost:4000
VITE_PYTHON_API_URL=http://localhost:8000
```

## Troubleshooting

### "Signature verification failed"
- **Issue**: JWT_SECRET mismatch between backends
- **Fix**: Ensure both `.env` files have identical `JWT_SECRET` value

### Chat endpoint returns 401
- **Issue**: Missing or invalid JWT token
- **Fix**: Make sure frontend sends `Authorization: Bearer <token>` header

### "Support system not initialized"
- **Issue**: Python backend failed to load LLM or vector store
- **Fix**: Check OPENROUTER_API_KEY and PDF_PATH in .env, review logs

### Database connection failed
- **Issue**: Supabase credentials incorrect
- **Fix**: Verify SUPABASE_URL and SUPABASE_ANON_KEY are correct

## Next Phases

### Phase 2: Core Features
- [ ] Implement product CRUD endpoints
- [ ] Implement order management endpoints
- [ ] Implement admin dashboard data endpoints
- [ ] Connect frontend Shop to product API
- [ ] Connect admin dashboard to real data

### Phase 3: Polish & Security
- [ ] Input validation on all endpoints (Zod/Joi)
- [ ] Rate limiting on auth endpoints
- [ ] Email verification for signup
- [ ] Admin audit logging
- [ ] Payment integration
- [ ] Cart management

## Directory Structure
```
.
├── backend-nodejs/          # Authentication & API gateway
│   ├── src/
│   │   ├── index.ts
│   │   ├── controllers/     # Auth handlers
│   │   ├── middleware/      # JWT verified, error handling
│   │   └── routes/
│   └── package.json
│
├── backend-python/          # AI support & LLM
│   ├── app/
│   │   ├── main.py         # FastAPI app & endpoints
│   │   ├── config.py
│   │   ├── services/       # LLM, memory, classifier
│   │   ├── models/         # Database models
│   │   └── utils/
│   ├── sql/                # Database schema
│   └── requirements.txt
│
├── lumina-sustainable-     # React frontend
│   fashion/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Route pages
│   │   ├── services/       # API calls, auth
│   │   └── context/        # React context
│   └── package.json
│
└── README.md
```

## Production Deployment

1. **Environment Variables**: Use production secrets (strong JWT_SECRET)
2. **CORS**: Configure allowed origins in Python backend
3. **Rate Limiting**: Updated values for production load
4. **Logging**: Monitor application logs for errors
5. **Database**: Use production Supabase instance
6. **LLM APIs**: Ensure OpenRouter API key has sufficient credits
7. **SSL/TLS**: Enable HTTPS for all production endpoints
8. **Docker**: Include Dockerfile for containerized deployment

## Support

For issues or questions:
1. Check logs in respective server terminals
2. Verify all environment variables are set correctly
3. Ensure all three services are running (Node.js, Python, React)
4. Review database schema matches your Supabase setup