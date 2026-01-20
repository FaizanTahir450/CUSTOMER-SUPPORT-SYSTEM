# security/security_manager.py
from security.sql_security import SQLSecurity
from security.prompt_security import PromptSecurity
from security.rate_limiter import RateLimiter

class SecurityManager:
    def __init__(self):
        self.sql_security = SQLSecurity()
        self.prompt_security = PromptSecurity()
        self.rate_limiter = RateLimiter()

    # -------------------------
    # User Input Security
    # -------------------------
    def validate_user_question(self, question: str) -> None:
        """
        Validate and sanitize user question.
        Raises ValueError if unsafe.
        """
        self.prompt_security.validate(question)

    # -------------------------
    # SQL Security
    # -------------------------
    def validate_generated_sql(self, sql: str) -> None:
        """
        Validate generated SQL query.
        Raises ValueError if unsafe.
        """
        self.sql_security.validate(sql)

    # -------------------------
    # Rate Limiting
    # -------------------------
    def check_rate_limit(self, client_id: str, endpoint: str) -> None:
        """
        Enforce rate limiting per client.
        """
        self.rate_limiter.check(client_id, endpoint)
