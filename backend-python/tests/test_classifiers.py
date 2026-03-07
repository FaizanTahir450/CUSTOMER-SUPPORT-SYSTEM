# tests/test_classifiers.py
import pytest
from unittest.mock import patch, Mock
from app.services.classifier import classify_query, classify_relevant_query


class TestClassifyQuery:
    """Test first-level message classification."""
    
    @patch('app.services.classifier.get_classification_llm')
    def test_classify_greeting(self, mock_get_llm, mock_llm):
        """Test detection of greetings."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content="greeting_smalltalk"))
        
        result = classify_query("hello, how are you")
        assert result == "greeting_smalltalk"
    
    @patch('app.services.classifier.get_classification_llm')
    def test_classify_irrelevant(self, mock_get_llm, mock_llm):
        """Test detection of irrelevant queries."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content="irrelevant"))
        
        result = classify_query("what's the weather?")
        assert result == "irrelevant"
    
    @patch('app.services.classifier.get_classification_llm')
    def test_classify_relevant(self, mock_get_llm, mock_llm):
        """Test detection of support-relevant queries."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content="relevant"))
        
        result = classify_query("where is my order?")
        assert result == "relevant"
    
    @patch('app.services.classifier.get_classification_llm')
    def test_classify_invalid_returns_irrelevant(self, mock_get_llm, mock_llm):
        """Test that invalid classifications default to irrelevant."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content="invalid_category"))
        
        result = classify_query("some message")
        assert result == "irrelevant"


class TestClassifyRelevantQuery:
    """Test second-level classification for relevant queries."""
    
    @patch('app.services.classifier.get_classification_llm')
    def test_classify_company_info(self, mock_get_llm, mock_llm):
        """Test detection of company info queries."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content="company_info"))
        
        result = classify_relevant_query("what's your return policy?")
        assert result == "company_info"
    
    @patch('app.services.classifier.get_classification_llm')
    def test_classify_order_related(self, mock_get_llm, mock_llm):
        """Test detection of order-related queries."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content="order_related"))
        
        result = classify_relevant_query("where is my order?")
        assert result == "order_related"
    
    @patch('app.services.classifier.get_classification_llm')
    def test_classify_invalid_returns_company_info(self, mock_get_llm, mock_llm):
        """Test that invalid classifications default to company_info."""
        mock_get_llm.return_value = mock_llm
        mock_llm.invoke = Mock(return_value=Mock(content="unknown"))
        
        result = classify_relevant_query("some query")
        assert result == "company_info"
