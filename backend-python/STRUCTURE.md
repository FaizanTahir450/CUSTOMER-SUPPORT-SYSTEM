# Backend Python Structure

## Directory Organization

```
backend-python/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # Flask/FastAPI application entry point
│   ├── config.py                 # Configuration settings
│   │
│   ├── models/                   # Data models and database schemas
│   │   ├── __init__.py
│   │   └── database.py           # Database models and initialization
│   │
│   ├── services/                 # Business logic and service layer
│   │   ├── __init__.py
│   │   ├── classifier.py         # Classification service
│   │   ├── db_service.py         # Database service operations
│   │   ├── llm.py                # LLM integration service
│   │   ├── memory.py             # Memory/cache service
│   │   ├── vector_store.py       # Vector database service
│   │   ├── graph.py              # Graph operations service
│   │   │
│   │   └── email/                # Email service submodule
│   │       ├── __init__.py
│   │       ├── poller.py         # Email polling service
│   │       └── gmail.py          # Gmail API integration
│   │
│   ├── api/                      # API routes and endpoints
│   │   └── __init__.py
│   │
│   └── utils/                    # Utility functions and helpers
│       └── __init__.py
│
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_*.py                 # Test files
│   └── __pycache__/
│
├── docs/                         # Documentation
│   ├── TESTING_GUIDE.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── QUICKSTART.md
│
├── logs/                         # Application logs (runtime)
│
├── scripts/                      # Utility scripts and migrations
│
├── chroma_db/                    # Vector database storage
│
├── .env                          # Environment variables
├── credentials.json              # API credentials
├── token.json                    # Auth tokens
├── customer_support.db           # SQLite database
├── requirements.txt              # Python dependencies
├── pytest.ini                    # Pytest configuration
├── run.py                        # Application entry point
├── setup.sh                      # Setup script
└── readme.md                     # Project documentation
```

## Folder Descriptions

### **app/** - Application Core
- **main.py**: Main Flask/FastAPI application initialization
- **config.py**: Configuration management and environment variables
- **models/**: Database models, schemas, and ORM definitions
- **services/**: Business logic, external integrations, and complex operations
  - **email/**: Email operations (polling, sending, Gmail integration)
  - Separate services for LLM, memory, vector store, classifiers, etc.
- **api/**: REST API endpoints and route handlers
- **utils/**: Helper functions, decorators, constants, and utilities

### **tests/** - Testing
- Unit tests, integration tests, and fixtures
- Uses pytest framework

### **docs/** - Documentation
- Testing guides
- Implementation details
- Quick start guides

### **logs/** - Runtime Logs
- Application debug and error logs

### **scripts/** - Database Migrations & Scripts
- Database migration scripts
- Utility scripts for maintenance

## How to Use

1. **Import modules**:
   ```python
   from app.services.classifier import classify_items
   from app.models.database import get_db_session
   from app.services.email.gmail import send_email
   ```

2. **Run application**:
   ```bash
   python run.py
   ```

3. **Run tests**:
   ```bash
   pytest
   ```

4. **Access documentation**:
   - See `docs/` folder for detailed guides

## Dependencies
- See `requirements.txt` for all Python dependencies
- Virtual environment in `venv/` folder
