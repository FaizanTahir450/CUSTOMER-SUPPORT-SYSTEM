# security/prompt_security.py
import re
import unicodedata

class PromptSecurity:
    MAX_LENGTH = 500

    INJECTION_PATTERNS = [
        r"ignore (all|previous) instructions",
        r"act as (system|developer)",
        r"you are not",
        r"reveal (prompt|system)",
        r"bypass",
        r"jailbreak",
        r"simulate",
        r"pretend to be",
        r"forget your role"
    ]

    def normalize(self, text: str) -> str:
        text = unicodedata.normalize("NFKC", text)
        return text.strip()

    def validate(self, question: str) -> None:
        if not question:
            raise ValueError("Question is empty")

        question = self.normalize(question)

        if len(question) > self.MAX_LENGTH:
            raise ValueError("Question too long")

        lowered = question.lower()

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lowered):
                raise ValueError("Prompt injection attempt detected")

        # Block control characters
        if any(ord(c) < 32 for c in question):
            raise ValueError("Invalid control characters detected")

        return None
