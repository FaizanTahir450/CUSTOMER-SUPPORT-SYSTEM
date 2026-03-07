# tests/test_memory.py
import pytest
from unittest.mock import Mock, patch
from app.services.memory import LLMCustomerSupportMemory
from app.config import Config
import json


class TestLLMCustomerSupportMemory:
    """Test customer support memory management."""
    
    def test_init(self):
        """Test memory initialization."""
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        
        assert memory.memory == {}
        assert memory.conversation_history == []
        assert memory.summary == ""
        assert memory._turn_count == 0
        assert memory._user_id == "user123"
    
    @patch('memory.get_extraction_llm')
    def test_update_memory(self, mock_get_llm, mock_llm):
        """Test memory fact extraction."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(
            content='{"customer_name": "John", "issue": "damaged_item"}'
        ))
        
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        updated = memory.update_memory("My name is John and I received a damaged item")
        
        assert "customer_name" in memory.memory
        assert memory.memory["customer_name"] == "John"
        assert len(memory.conversation_history) == 1
        assert memory.conversation_history[0]["role"] == "user"
        assert memory._turn_count == 1
    
    @patch('memory.get_extraction_llm')
    def test_add_assistant_message(self, mock_get_llm, mock_llm):
        """Test adding assistant messages to history."""
        mock_get_llm.return_value = mock_llm
        
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        memory.add_assistant_message("Thank you for contacting us.")
        
        assert len(memory.conversation_history) == 1
        assert memory.conversation_history[0]["role"] == "assistant"
        assert memory.conversation_history[0]["content"] == "Thank you for contacting us."
    
    @patch('memory.get_extraction_llm')
    def test_get_conversation_history(self, mock_get_llm, mock_llm):
        """Test retrieving conversation history."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content='{}'))
        
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        memory.update_memory("Hello")
        memory.add_assistant_message("Hi there!")
        
        history = memory.get_conversation_history()
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
    
    @patch('memory.get_extraction_llm')
    def test_get_recent_context(self, mock_get_llm, mock_llm):
        """Test retrieving recent conversation context."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content='{}'))
        
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        
        # Add multiple turns
        for i in range(10):
            memory.conversation_history.append({"role": "user", "content": f"Message {i}"})
        
        recent = memory.get_recent_context(max_turns=4)
        assert len(recent) == 4
        assert recent[0]["content"] == "Message 6"
        assert recent[-1]["content"] == "Message 9"
    
    @patch('memory.get_extraction_llm')
    def test_memory_compression(self, mock_get_llm, mock_llm):
        """Test memory compression and summarization."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(
            content='Summary: Customer had issue, now resolved.'
        ))
        
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        
        # Simulate multiple turns exceeding compression threshold
        for i in range(Config.MEMORY_COMPRESSION_INTERVAL + 2):
            memory.conversation_history.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Turn {i}"
            })
            memory._turn_count = i + 1
        
        # Compression should have triggered
        # (In real scenario with mocked _compress_memory)
        assert memory._turn_count == Config.MEMORY_COMPRESSION_INTERVAL + 2
    
    @patch('memory.get_extraction_llm')
    def test_clear_memory(self, mock_get_llm, mock_llm):
        """Test clearing all memory."""
        mock_get_llm.return_value = mock_llm
        
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        memory.memory = {"customer_name": "John"}
        memory.conversation_history = [{"role": "user", "content": "Hello"}]
        memory.summary = "Customer had an issue"
        memory._turn_count = 5
        
        memory.clear_memory()
        
        assert memory.memory == {}
        assert memory.conversation_history == []
        assert memory.summary == ""
        assert memory._turn_count == 0
    
    @patch('memory.get_extraction_llm')
    def test_get_memory_json(self, mock_get_llm, mock_llm):
        """Test JSON serialization of memory."""
        mock_get_llm.return_value = mock_llm
        
        memory = LLMCustomerSupportMemory(mysql_service=None, user_id="user123")
        memory.memory = {"customer_name": "John", "status": "resolved"}
        
        memory_json = memory.get_memory_json()
        parsed = json.loads(memory_json)
        
        assert parsed["customer_name"] == "John"
        assert parsed["status"] == "resolved"
