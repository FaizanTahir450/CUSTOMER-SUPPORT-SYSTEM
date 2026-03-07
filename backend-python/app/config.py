# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Supabase / PostgreSQL ────────────────────────────────────────────────
    # Transaction-pooler connection string from Supabase dashboard
    # Format: postgresql+psycopg2://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
    SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")

    # ── OpenRouter ───────────────────────────────────────────────────────────
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    MODEL_NAME         = os.getenv("MODEL_NAME", "google/gemini-2.0-flash")
    CLASSIFICATION_MODEL = os.getenv("CLASSIFICATION_MODEL", "openai/gpt-4o-mini")  # cheaper model for classification
    EXTRACTION_MODEL = os.getenv("EXTRACTION_MODEL", "openai/gpt-4o-mini")  # cheaper model for extraction

    # ── PDF ──────────────────────────────────────────────────────────────────
    PDF_PATH = os.getenv("PDF_PATH", "Lama1.pdf")

    # ── Gmail ────────────────────────────────────────────────────────────────
    # Path to the OAuth2 credentials JSON downloaded from Google Cloud Console
    GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")

    # Path where the OAuth2 token will be saved after first browser login
    GMAIL_TOKEN_PATH       = os.getenv("GMAIL_TOKEN_PATH", "token.json")

    # Display name shown in the "From" field of outgoing emails
    GMAIL_SENDER_NAME      = os.getenv("GMAIL_SENDER_NAME", "support@lamaretail.com")

    # How often (seconds) to poll Gmail for new unread emails
    GMAIL_POLL_INTERVAL    = int(os.getenv("GMAIL_POLL_INTERVAL", "15"))

    # ── API Security ─────────────────────────────────────────────────────────
    API_KEY = os.getenv("API_KEY", "")  # Required for /chat endpoint
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "15"))

    # ── LangSmith Observability ──────────────────────────────────────────────
    LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
    LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    LANGFUSE_ENABLED = os.getenv("LANGFUSE_ENABLED", "False").lower() == "true"

    # ── Memory Compression ───────────────────────────────────────────────────
    MEMORY_COMPRESSION_INTERVAL = int(os.getenv("MEMORY_COMPRESSION_INTERVAL", "10"))  # Summarize every N turns

    # ── Logging ──────────────────────────────────────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def validate():
        """Validate all required config variables are set. Raises EnvironmentError if any are missing."""
        required_vars = {
            "OPENROUTER_API_KEY": Config.OPENROUTER_API_KEY,
            "SUPABASE_DB_URL":    Config.SUPABASE_DB_URL,
        }
        
        optional_but_recommended = {
            "API_KEY": Config.API_KEY,
            "LANGFUSE_SECRET_KEY": Config.LANGFUSE_SECRET_KEY,
        }

        missing_required = [k for k, v in required_vars.items() if not v]
        if missing_required:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing_required)}\n"
                f"Please set them in your .env file or as environment variables."
            )

        warnings = []
        for k, v in optional_but_recommended.items():
            if not v:
                warnings.append(f"⚠️  {k} not set — some features may be limited")
        
        if warnings:
            for warning in warnings:
                print(warning)