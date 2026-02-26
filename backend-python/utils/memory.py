import json
from typing import Dict, Any
from services.llm import get_extraction_llm  # Your existing LLM instance

class LLMCustomerSupportMemory:
    """
    Memory module for customer support chatbot.
    Uses a centralized extraction LLM from llm.py.
    Includes robust JSON parsing and utility methods.
    """
    
    def __init__(self):
        self.memory: Dict[str, Any] = {}
        self.conversation_history: list = []
        # Use your existing LLM instance
        self.llm = get_extraction_llm()
    
    def _create_extraction_prompt(self, user_message: str) -> str:
        """Creates prompt for fact extraction from user message."""
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
        """Extract JSON from text even if extra content is present."""
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
        return {}
    
    def update_memory(self, user_message: str) -> Dict[str, Any]:
        """Process message through LLM, update memory, and return new/updated facts."""
        self.conversation_history.append(user_message)
        
        prompt = self._create_extraction_prompt(user_message)
        llm_response = self.llm.invoke(prompt).content  # Using your LLM instance
        
        # Clean up response and parse JSON
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
        
        return updated_facts
    
    def get_memory(self) -> Dict[str, Any]:
        """Return a copy of the current memory."""
        return self.memory.copy()
    
    def get_memory_json(self) -> str:
        """Return memory as a JSON string."""
        return json.dumps(self.memory, indent=2)
    
    def clear_memory(self):
        """Clear memory and conversation history."""
        self.memory = {}
        self.conversation_history = []
    
    def get_conversation_history(self) -> list:
        """Return all messages in the conversation."""
        return self.conversation_history.copy()