# security/sql_security.py
import re

class SQLSecurity:
    """
    Enforces strict read-only SQL policy.
    """

    FORBIDDEN_KEYWORDS = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER",
        "CREATE", "TRUNCATE", "REPLACE", "MERGE",
        "GRANT", "REVOKE", "LOCK", "UNLOCK",
        "INTO OUTFILE", "LOAD_FILE",
        "INFORMATION_SCHEMA", "MYSQL.", "PERFORMANCE_SCHEMA",
        "SLEEP(", "BENCHMARK("
    ]

    COMMENT_PATTERNS = [
        r"--",
        r"/\*",
        r"\*/"
    ]

    def validate(self, query: str) -> None:
        if not query:
            raise ValueError("Empty SQL query")

        normalized = query.upper().strip()

        # Must start with SELECT or WITH
        if not (normalized.startswith("SELECT") or normalized.startswith("WITH")):
            raise ValueError("Only SELECT queries are allowed")

        # No multiple statements
        if ";" in normalized:
            raise ValueError("Multiple SQL statements are not allowed")

        # Block comments
        for pattern in self.COMMENT_PATTERNS:
            if re.search(pattern, normalized):
                raise ValueError("SQL comments are not allowed")

        # Block forbidden keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in normalized:
                raise ValueError(f"Forbidden SQL operation detected: {keyword}")

        # Basic length limit
        if len(query) > 2000:
            raise ValueError("SQL query too long")

        return None
