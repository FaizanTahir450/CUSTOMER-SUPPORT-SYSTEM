# db.py
from mysql_service import MySQLService
from typing import Optional

# Global MySQL service instance
_mysql_service: Optional[MySQLService] = None

def init_database():
    """Initialize MySQL connection (no auto-creation of sample data)"""
    global _mysql_service
    
    try:
        _mysql_service = MySQLService()
        
        # Test connection
        if _mysql_service.test_connection():
            print("✅ MySQL database connected successfully")
            
            # Print available schema for debugging
            schema = _mysql_service.get_database_schema()
            if schema:
                print("\n📋 Database Schema:")
                print("=" * 50)
                print(schema)
                print("=" * 50)
        else:
            print("❌ MySQL connection test failed")
            
    except Exception as e:
        print(f"❌ Error initializing MySQL: {e}")
        raise

def get_mysql_service() -> MySQLService:
    """Get the global MySQL service instance"""
    global _mysql_service
    
    if _mysql_service is None:
        init_database()
    
    return _mysql_service

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
        # Query to get all orders for the user
        sql_query = f"""
        SELECT 
            order_id,
            status,
            total,
            created_at
        FROM orders
        WHERE user_id = '{user_id}'
        ORDER BY created_at DESC
        """
        
        results, error = mysql_service.execute_query(sql_query)
        
        if error:
            print(f"❌ Database query error: {error}")
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
        print(f"❌ Error querying database: {e}")
        return ""

def close_database():
    """Close MySQL connection"""
    global _mysql_service
    
    if _mysql_service:
        _mysql_service.close()
        print("✅ MySQL connection closed")