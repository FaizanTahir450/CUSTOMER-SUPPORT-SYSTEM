# memory.py
import json
from typing import Dict, Any, Optional
from app.services.llm import get_extraction_llm
from app.config import Config
import logging

logger = logging.getLogger(__name__)


class LLMCustomerSupportMemory:

    def __init__(self, mysql_service=None, user_id: Optional[str] = None):
        self.memory: Dict[str, Any] = {}
        self.conversation_history: list = []  # Full message history: [{"role": "user/assistant", "content": "..."}, ...]
        self.summary: str = ""  # Compressed summary of old conversations
        self.llm = get_extraction_llm()
        self._mysql_service = mysql_service
        self._user_id = user_id
        self._turn_count = 0  # Track conversation turns for compression

    # ── DB: load once at session start ──────────────────────────────

    def load_from_db(self) -> None:
        """Load memory from users table into RAM. Called once when session starts."""
        if not self._mysql_service or not self._user_id:
            return
        try:
            from sqlalchemy import text
            with self._mysql_service.engine.connect() as conn:
                row = conn.execute(
                    text("SELECT memory FROM users WHERE user_id = :uid LIMIT 1"),
                    {"uid": self._user_id}
                ).fetchone()

            if row and row[0]:
                self.memory = json.loads(row[0])
                logger.info(f"Memory loaded from DB for user '{self._user_id}'")
            else:
                logger.info(f"No existing memory for user '{self._user_id}', starting fresh")

        except Exception as e:
            logger.error(f"Could not load memory from DB: {e}")

    # ── DB: save on every memory update ─────────────────────────────

    def _save_to_db(self) -> None:
        """Push current RAM memory back to the users table."""
        if not self._mysql_service or not self._user_id:
            return
        try:
            from sqlalchemy import text
            memory_json = json.dumps(self.memory, ensure_ascii=False)

            with self._mysql_service.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO users (user_id, memory)
                        VALUES (:uid, :mem)
                    ON CONFLICT (user_id) DO UPDATE SET
                        memory     = EXCLUDED.memory,
                        updated_at = CURRENT_TIMESTAMP
                """), {"uid": self._user_id, "mem": memory_json})
                conn.commit()
            logger.debug(f"Memory saved to DB for user '{self._user_id}'")

        except Exception as e:
            logger.error(f"Could not save memory to DB: {e}")

    # ── Memory compression ──────────────────────────────────────────

    def _should_compress(self) -> bool:
        """Check if it's time to compress conversation history."""
        return self._turn_count > 0 and self._turn_count % Config.MEMORY_COMPRESSION_INTERVAL == 0

    def _compress_memory(self) -> None:
        """Summarize old turns and keep recent ones for context."""
        if len(self.conversation_history) < 4:
            return  # Not enough to compress
        
        logger.info(f"Compressing memory for user '{self._user_id}' ({len(self.conversation_history)} turns)")
        
        # Keep last 4 turns, compress the rest
        recent_turns = self.conversation_history[-4:]
        old_turns = self.conversation_history[:-4]
        
        if not old_turns:
            return
        
        old_text = "\n".join([f"{t['role']}: {t['content']}" for t in old_turns])
        
        compress_prompt = f"""Summarize the following conversation concisely in 2-3 sentences, 
capturing key customer needs, issues, and any decisions made:

{old_text}

Summary:"""
        
        try:
            summary_response = self.llm.invoke(compress_prompt).content
            self.summary = summary_response
            self.conversation_history = recent_turns
            logger.debug(f"Compression complete: {len(old_turns)} turns summarized, {len(recent_turns)} recent turns kept")
        except Exception as e:
            logger.error(f"Failed to compress memory: {e}")

    # ── Core logic (enhanced with conversation history) ──────────────

    def _create_extraction_prompt(self, user_message: str) -> str:
        current_memory_str = json.dumps(self.memory, indent=2) if self.memory else "Empty"
        return f"""You are a fact extraction system for a customer support chatbot.

Analyze the user's message and extract ALL relevant facts as structured data.

Current Memory:
{current_memory_str}

User message: "{user_message}"

Instructions:
1. Extract ALL facts (names, product details, issues, intent, emotions, urgency, order info, etc.)
2. Use clear, descriptive field names (e.g., "customer_name", "issue_description")
3. Include updates to existing facts if needed
4. Return ONLY a valid JSON object

Example output:
{{
  "customer_name": "John Doe",
  "product_type": "laptop",
  "issue_description": "screen flickering",
  "customer_emotion": "frustrated",
  "urgency_level": "high"
}}

Extract facts now:"""

    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        return {}

    def update_memory(self, user_message: str) -> Dict[str, Any]:
        """Extract facts from message, update RAM memory, compress if needed."""
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        self._turn_count += 1

        prompt = self._create_extraction_prompt(user_message)
        llm_response = self.llm.invoke(prompt).content

        if "```json" in llm_response:
            llm_response = llm_response.split("```json")[1].split("```")[0].strip()
        elif "```" in llm_response:
            llm_response = llm_response.split("```")[1].split("```")[0].strip()

        try:
            extracted_facts = json.loads(llm_response)
        except json.JSONDecodeError:
            extracted_facts = self._extract_json_from_text(llm_response)

        updated_facts = {}
        for key, value in extracted_facts.items():
            if key not in self.memory or self.memory[key] != value:
                updated_facts[key] = value
                self.memory[key] = value

        # Push updated memory to DB immediately
        self._save_to_db()

        # Check if compression is needed
        if self._should_compress():
            self._compress_memory()

        return updated_facts

    def add_assistant_message(self, assistant_response: str) -> None:
        """Add assistant response to conversation history."""
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })
        logger.debug(f"Added assistant message to history for user '{self._user_id}'")

    def get_memory(self) -> Dict[str, Any]:
        return self.memory.copy()

    def get_memory_json(self) -> str:
        return json.dumps(self.memory, indent=2)

    def get_conversation_history(self) -> list:
        """Return full conversation history for LLM context."""
        return self.conversation_history.copy()

    def get_recent_context(self, max_turns: int = 8) -> list:
        """Return the most recent N turns of conversation for context window optimization."""
        return self.conversation_history[-max_turns:]

    def clear_memory(self) -> None:
        self.memory = {}
        self.conversation_history = []
        self.summary = ""
        self._turn_count = 0
        self._save_to_db()  # wipe DB memory too
        logger.info(f"Memory cleared for user '{self._user_id}'")