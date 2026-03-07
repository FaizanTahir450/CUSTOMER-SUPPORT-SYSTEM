# database.py
from app.services.db_service import SupabaseService
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Global Supabase service instance
_db_service: Optional[SupabaseService] = None

def init_database():
    """Initialize Supabase (PostgreSQL) connection"""
    global _db_service
    
    try:
        _db_service = SupabaseService()
        
        if _db_service.test_connection():
            logger.info("Supabase database connected successfully")
            
            schema = _db_service.get_database_schema()
            if schema:
                logger.info("Database Schema: " + "=" * 50 + "\n" + schema + "\n" + "=" * 50)
        else:
            logger.error("Supabase connection test failed")
            
    except Exception as e:
        logger.error(f"Error initializing Supabase: {e}")
        raise

def get_mysql_service() -> SupabaseService:
    """Get the global database service instance (Supabase/PostgreSQL)."""
    global _db_service
    
    if _db_service is None:
        init_database()
    
    return _db_service

def get_order_info(user_id: str, query: str) -> str:
    """
    Fetch order information for a user from MySQL database.
    
    Args:
        user_id: The user's ID
        query: The user's question (not used directly, but kept for compatibility)
    
    Returns:
        Formatted string with order information or empty string if no orders found
    """
    mysql_service = get_mysql_service()
    
    try:
        results, error = mysql_service.execute_query_safe(
            """
            SELECT order_id, status, total, created_at
            FROM orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            """,
            {"user_id": user_id},
        )
        
        if error:
            logger.error(f"Database query error: {error}")
            return ""
        
        if not results:
            return ""
        
        # Format order information
        order_info = []
        for order in results:
            order_info.append(
                f"Order ID: {order['order_id']}, "
                f"Status: {order['status']}, "
                f"Total: ${float(order['total']):.2f}, "
                f"Date: {order['created_at'].strftime('%Y-%m-%d') if hasattr(order['created_at'], 'strftime') else str(order['created_at'])}"
            )
        
        return "\n".join(order_info)
    
    except Exception as e:
        logger.error(f"Error querying database: {e}")
        return ""


def get_orders(user_id: str):
    """Return raw list of orders for the user (list of dicts) or (None, error)."""
    mysql_service = get_mysql_service()
    try:
        results, error = mysql_service.execute_query_safe(
            """
            SELECT order_id, status, total, created_at
            FROM orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            """,
            {"user_id": user_id},
        )
        return results, error
    except Exception as e:
        return None, str(e)


def cancel_order(order_id: str, user_id: str) -> tuple[bool, str | None]:
    """Attempt to cancel an order. Returns (success, error_message).

    Uses `SupabaseService.cancel_order` which only updates when status is pending.
    """
    mysql_service = get_mysql_service()
    try:
        success, error = mysql_service.cancel_order(order_id, user_id)
        return success, error
    except Exception as e:
        return False, str(e)

def close_database():
    """Close database connection"""
    global _db_service
    
    if _db_service:
        _db_service.close()
        logger.info("Supabase connection closed")