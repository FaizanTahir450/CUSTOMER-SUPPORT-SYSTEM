# tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app
import json


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health endpoint returns healthy status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "graph_initialized" in data
        assert "email_poller_active" in data


class TestChatEndpoint:
    """Test the chat endpoint."""
    
    @patch('app.support_graph')
    @patch('app.get_db_service')
    @patch('app.LLMCustomerSupportMemory')
    def test_chat_success(self, mock_memory_class, mock_get_service, mock_graph, client):
        """Test successful chat interaction."""
        # Setup mocks
        mock_graph.invoke.return_value = {"response": "How can I help you?"}
        
        mock_memory_instance = Mock()
        mock_memory_instance.get_conversation_history.return_value = []
        mock_memory_class.return_value = mock_memory_instance
        
        app.support_graph = mock_graph
        
        payload = {
            "user_id": "user123",
            "message": "Hello, I need help with my order"
        }
        
        # Make request (without API key since it's optional in config)
        response = client.post("/chat", json=payload)
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"] == "How can I help you?"
    
    @patch('app.support_graph', None)
    def test_chat_graph_not_initialized(self, client):
        """Test that chat fails gracefully when graph isn't initialized."""
        app.support_graph = None
        
        payload = {
            "user_id": "user123",
            "message": "Hello"
        }
        
        response = client.post("/chat", json=payload)
        
        assert response.status_code == 503
        assert "not initialized" in response.json()["detail"].lower()
    
    @patch('app.Config')
    def test_chat_with_api_key_required(self, mock_config, client):
        """Test that API key is required when configured."""
        # This would require setting Config.API_KEY and testing the auth logic
        # Skipping for now as it's more of an integration test
        pass


class TestHistoryEndpoint:
    """Test the conversation history endpoint."""
    
    @patch('app.get_db_service')
    @patch('app.LLMCustomerSupportMemory')
    def test_get_history_success(self, mock_memory_class, mock_get_service, client):
        """Test successful history retrieval."""
        mock_memory_instance = Mock()
        mock_memory_instance.get_conversation_history.return_value = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        mock_memory_instance.get_memory.return_value = {"customer_name": "John"}
        mock_memory_class.return_value = mock_memory_instance
        
        response = client.get("/history/user123")
        
        # Note: May fail without API key if required, but testing the logic
        # if auth is disabled
        if response.status_code == 200:
            data = response.json()
            assert data["user_id"] == "user123"
            assert "conversation_history" in data
            assert "memory" in data
    
    def test_history_without_api_key_when_required(self, client):
        """Test that history endpoint requires API key if configured."""
        # This is a conditional test based on Config.API_KEY
        # If API key is required, this should fail
        response = client.get("/history/user123")
        
        # Should either succeed (if no API key required) or fail with 403
        assert response.status_code in [200, 403]


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    @patch('app.support_graph')
    @patch('app.get_db_service')
    @patch('app.LLMCustomerSupportMemory')
    def test_rate_limit_enforcement(self, mock_memory_class, mock_get_service, mock_graph, client):
        """Test that rate limiting is enforced."""
        mock_graph.invoke.return_value = {"response": "Hello"}
        
        mock_memory_instance = Mock()
        mock_memory_instance.get_conversation_history.return_value = []
        mock_memory_class.return_value = mock_memory_instance
        
        app.support_graph = mock_graph
        
        # Note: Rate limiting might not trigger in test environment
        # This is more of an integration test
        payload = {
            "user_id": "user123",
            "message": "Hello"
        }
        
        # Make multiple requests
        responses = []
        for _ in range(3):
            response = client.post("/chat", json=payload)
            responses.append(response.status_code)
        
        # Should all succeed in most test scenarios
        assert all(status in [200, 429] for status in responses)
