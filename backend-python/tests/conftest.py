# tests/conftest.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from config import Config
import os
import tempfile

@pytest.fixture
def mock_llm():
    """Mock LLM that returns predetermined responses."""
    mock = Mock()
    
    def sides_effect(prompt: str):
        response = Mock()
        
        # Classify queries
        if "greeting_smalltalk" in prompt:
            response.content = "greeting_smalltalk"
        elif "irrelevant" in prompt:
            response.content = "irrelevant"
        elif "relevant" in prompt:
            response.content = "relevant"
        elif "company_info" in prompt:
            response.content = "company_info"
        elif "order_related" in prompt:
            response.content = "order_related"
        # Extract facts
        elif "fact extraction" in prompt.lower():
            response.content = '{"customer_emotion": "satisfied", "issue_resolved": true}'
        # Default response
        else:
            response.content = "Thank you for contacting Lama Retail support."
        
        return response
    
    mock.invoke = sides_effect
    return mock

@pytest.fixture
def mock_mysql_service():
    """Mock MySQL service."""
    mock = Mock()
    mock.engine = Mock()
    mock.test_connection.return_value = True
    return mock

@pytest.fixture
def temp_env():
    """Create temporary .env file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
        f.write("OPENROUTER_API_KEY=test_key\n")
        f.write("MYSQL_PASSWORD=test_password\n")
        f.write("API_KEY=test_api_key\n")
        temp_file = f.name
    
    yield temp_file
    
    if os.path.exists(temp_file):
        os.unlink(temp_file)

@pytest.fixture
def mock_memory():
    """Mock LLMCustomerSupportMemory."""
    mock = Mock()
    mock.memory = {"customer_name": "John Doe"}
    mock.conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    mock.get_memory.return_value = {"customer_name": "John Doe"}
    mock.get_memory_json.return_value = '{"customer_name": "John Doe"}'
    mock.get_conversation_history.return_value = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    mock.get_recent_context.return_value = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi there!"}
    ]
    mock.update_memory = Mock()
    mock.add_assistant_message = Mock()
    return mock
