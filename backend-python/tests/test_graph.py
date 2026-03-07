# tests/test_graph.py
import pytest
from unittest.mock import Mock, patch
from app.services.graph import create_support_graph, _build_conversation_context
from typing import List


class TestGraphHelpers:
    """Test graph utility functions."""
    
    def test_build_conversation_context_empty(self):
        """Test building context from empty history."""
        context = _build_conversation_context([])
        assert context == ""
    
    def test_build_conversation_context_with_turns(self):
        """Test building context from conversation history."""
        history = [
            {"role": "user", "content": "What are your hours?"},
            {"role": "assistant", "content": "We're open 9am-6pm daily."}
        ]
        
        context = _build_conversation_context(history)
        
        assert "Customer: What are your hours?" in context
        assert "Sophia (support): We're open 9am-6pm daily." in context
    
    def test_build_conversation_context_respects_max_turns(self):
        """Test that context respects max_turns parameter."""
        history = [
            {"role": "user", "content": f"Message {i}"} for i in range(10)
        ]
        
        context = _build_conversation_context(history, max_turns=3)
        
        # Should only include last 3
        assert "Message 7" in context
        assert "Message 8" in context
        assert "Message 9" in context


class TestSupportGraph:
    """Test the support graph structure and routing."""
    
    @patch('graph.get_llm')
    @patch('graph.classify_query')
    @patch('graph.classify_relevant_query')
    @patch('graph.search_company_info')
    @patch('graph.get_orders')
    @patch('graph.cancel_order')
    def test_graph_creation(self, mock_cancel, mock_orders, mock_search, 
                           mock_sub_classify, mock_classify, mock_get_llm):
        """Test that graph is created successfully."""
        # Mock LLM
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(content="Thank you for contacting us."))
        mock_get_llm.return_value = mock_llm
        
        graph = create_support_graph()
        
        # Should return a compiled graph
        assert graph is not None
        assert callable(graph.invoke)
    
    @patch('graph.get_llm')
    @patch('graph.classify_query')
    @patch('graph.LLMCustomerSupportMemory')
    def test_classify_node(self, mock_memory_class, mock_classify, mock_get_llm):
        """Test classify node."""
        from graph import classify_node, SupportState
        
        mock_classify.return_value = "greeting_smalltalk"
        
        state = {
            "user_id": "user123",
            "message": "hello",
            "response": "",
            "classification": "",
            "sub_classification": "",
            "context": "",
            "memory": Mock(),
            "conversation_history": []
        }
        
        result = classify_node(state)
        
        assert result["classification"] == "greeting_smalltalk"
        mock_classify.assert_called_once()
    
    @patch('graph.get_llm')
    @patch('graph.LLMCustomerSupportMemory')
    def test_handle_greeting_node(self, mock_memory, mock_get_llm):
        """Test greeting handling node."""
        from graph import handle_greeting
        
        mock_llm = Mock()
        mock_response = Mock(content="Hello! How can I help you?")
        mock_llm.invoke = Mock(return_value=mock_response)
        mock_get_llm.return_value = mock_llm
        
        memory = Mock()
        memory.get_memory_json.return_value = "{}"
        memory.add_assistant_message = Mock()
        memory.get_conversation_history = Mock(return_value=[])
        
        state = {
            "user_id": "user123",
            "message": "hi",
            "response": "",
            "classification": "greeting_smalltalk",
            "sub_classification": "",
            "context": "",
            "memory": memory,
            "conversation_history": []
        }
        
        result = handle_greeting(state)
        
        assert result["response"] == "Hello! How can I help you?"
        memory.add_assistant_message.assert_called_once()
    
    @patch('graph.get_llm')
    @patch('graph.LLMCustomerSupportMemory')
    def test_handle_irrelevant_node(self, mock_memory, mock_get_llm):
        """Test irrelevant query handling."""
        from graph import handle_irrelevant
        
        memory = Mock()
        memory.add_assistant_message = Mock()
        memory.get_conversation_history = Mock(return_value=[])
        
        state = {
            "user_id": "user123",
            "message": "what's the weather?",
            "response": "",
            "classification": "irrelevant",
            "sub_classification": "",
            "context": "",
            "memory": memory,
            "conversation_history": []
        }
        
        result = handle_irrelevant(state)
        
        assert "customer support assistant" in result["response"]
        memory.add_assistant_message.assert_called_once()
    
    @patch('graph.classify_query')
    def test_route_after_classification_greeting(self, mock_classify):
        """Test routing after classification for greetings."""
        from graph import route_after_classification
        
        state = {
            "classification": "greeting_smalltalk",
            "message": "hello"
        }
        
        route = route_after_classification(state)
        assert route == "greeting"
    
    @patch('graph.classify_query')
    def test_route_after_classification_irrelevant(self, mock_classify):
        """Test routing after classification for irrelevant queries."""
        from graph import route_after_classification
        
        state = {
            "classification": "irrelevant",
            "message": "random text"
        }
        
        route = route_after_classification(state)
        assert route == "irrelevant"
    
    @patch('graph.classify_query')
    def test_route_after_classification_relevant(self, mock_classify):
        """Test routing after classification for relevant queries."""
        from graph import route_after_classification
        
        state = {
            "classification": "relevant",
            "message": "I need help"
        }
        
        route = route_after_classification(state)
        assert route == "extract_memory"
    
    def test_route_after_sub_classification_company_info(self):
        """Test routing to company info handler."""
        from graph import route_after_sub_classification
        
        state = {
            "sub_classification": "company_info"
        }
        
        route = route_after_sub_classification(state)
        assert route == "check_memory"
    
    def test_route_after_sub_classification_order_related(self):
        """Test routing to database handler."""
        from graph import route_after_sub_classification
        
        state = {
            "sub_classification": "order_related"
        }
        
        route = route_after_sub_classification(state)
        assert route == "query_database"
