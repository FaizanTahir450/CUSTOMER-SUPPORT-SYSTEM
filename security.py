

import bleach
import re


ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}

def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input using bleach to prevent XSS attacks.
    Strips all HTML tags and attributes.
    """
    return bleach.clean(
        user_input,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

def validate_query_length(user_input: str, min_length: int = 1, max_length: int = 200) -> bool:
    """
    Validate that input length is within allowed range.
    Helps prevent resource exhaustion attacks.
    """
    user_input = user_input.strip()
    return min_length <= len(user_input) <= max_length

def detect_sql_injection(user_input: str) -> bool:
    """
    Basic SQL injection pattern detection.
    This looks for common dangerous SQL keywords.
    """
    sql_keywords = [
        "select", "insert", "update", "delete", "drop", "union",
        "--", ";", "/*", "*/", "xp_", "exec", "or 1=1", "' or '1'='1"
    ]
    pattern = r"|".join(re.escape(word) for word in sql_keywords)
    return bool(re.search(pattern, user_input, re.IGNORECASE))

def contains_control_characters(user_input: str) -> bool:
    """
    Check for dangerous non-printable or control characters in user input.
    Blocks null bytes, special control sequences, etc.
    """
    return any(ord(c) < 32 and c not in ('\n', '\r', '\t') for c in user_input)

def validate_and_sanitize(user_input: str) -> str:
    """
    Complete Guardrail Pipeline:
    - Length check
    - Non-printable character check
    - SQL Injection keyword check
    - Final XSS sanitization
    Returns cleaned and safe input.
    Raises ValueError on validation failure.
    """
    user_input = user_input.strip()

   
    if not validate_query_length(user_input):
        raise ValueError(f"❌ Query length must be between 1 and 200 characters. Received length: {len(user_input)}")

   
    if contains_control_characters(user_input):
        raise ValueError("❌ Query contains non-printable or control characters.")

  
    if detect_sql_injection(user_input):
        raise ValueError("❌ Query contains suspicious SQL keywords or SQL injection patterns.")

   
    sanitized = sanitize_input(user_input)

    return sanitized
