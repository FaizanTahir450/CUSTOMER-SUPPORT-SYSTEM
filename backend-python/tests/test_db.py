# tests/test_db.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.models.database import get_orders, cancel_order, get_db_service
from datetime import datetime


class TestDatabaseOperations:
    """Test database helper functions."""
    
    @patch('app.models.database.get_mysql_service')
    def test_get_orders_success(self, mock_get_service):
        """Test successful order retrieval."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_orders = [
            {
                'order_id': '001',
                'status': 'pending',
                'total': '99.99',
                'created_at': datetime(2025, 1, 1)
            },
            {
                'order_id': '002',
                'status': 'shipped',
                'total': '49.99',
                'created_at': datetime(2025, 1, 2)
            }
        ]
        
        mock_service.execute_query_safe.return_value = (mock_orders, None)
        
        orders, error = get_orders('user123')
        
        assert orders == mock_orders
        assert error is None
        assert len(orders) == 2
    
    @patch('app.models.database.get_mysql_service')
    def test_get_orders_empty(self, mock_get_service):
        """Test order retrieval when no orders exist."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.execute_query_safe.return_value = ([], None)
        
        orders, error = get_orders('user_no_orders')
        
        assert orders == []
        assert error is None
    
    @patch('app.models.database.get_mysql_service')
    def test_get_orders_error(self, mock_get_service):
        """Test error handling in order retrieval."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.execute_query_safe.return_value = (None, "Database error")
        
        orders, error = get_orders('user123')
        
        assert orders is None
        assert error == "Database error"
    
    @patch('app.models.database.get_mysql_service')
    def test_cancel_order_success(self, mock_get_service):
        """Test successful order cancellation."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.cancel_order.return_value = (True, None)
        
        success, error = cancel_order('order001', 'user123')
        
        assert success is True
        assert error is None
    
    @patch('app.models.database.get_mysql_service')
    def test_cancel_order_not_found(self, mock_get_service):
        """Test cancellation when order not found."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.cancel_order.return_value = (
            False,
            "Order not in pending state or not found for this user"
        )
        
        success, error = cancel_order('nonexistent', 'user123')
        
        assert success is False
        assert "not found" in error
    
    @patch('app.models.database.get_mysql_service')
    def test_cancel_order_permission_denied(self, mock_get_service):
        """Test cancellation with permission issues."""
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        mock_service.cancel_order.return_value = (
            False,
            "Order belongs to different user"
        )
        
        success, error = cancel_order('order001', 'wrong_user')
        
        assert success is False
        assert "different user" in error
