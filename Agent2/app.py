from flask import Flask, render_template, request, jsonify, session
from mysql_service import MySQLService
from gemini_service import GeminiService
from config import Config
import json
from typing import Dict, Any
from security.security_manager import SecurityManager
app = Flask(__name__)
app.config.from_object(Config)

# Initialize services
mysql_service = None
gemini_service = None
security_manager = SecurityManager()

def get_client_id():
    return request.remote_addr or "unknown"

try:
    mysql_service = MySQLService()
except Exception as e:
    print(f"Failed to initialize MySQL service: {e}")

try:
    gemini_service = GeminiService()
except Exception as e:
    print(f"Failed to initialize Gemini service: {e}")

@app.route('/')
def index():
    """Main page"""
    connection_status = mysql_service.test_connection() if mysql_service else False
    return render_template('index.html', 
                         connection_status=connection_status,
                         gemini_available=gemini_service is not None)

@app.route('/api/schema')
def get_schema():
    """Get database schema"""
    if not mysql_service:
        return jsonify({'error': 'MySQL service not available'}), 500
    
    try:
        security_manager.check_rate_limit(get_client_id(), "/api/schema")
        schema = mysql_service.get_database_schema()
        return jsonify({'schema': schema})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def execute_query():
    """Execute natural language query"""
    if not mysql_service or not gemini_service:
        return jsonify({'error': 'Services not available'}), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get database schema
        schema = mysql_service.get_database_schema()
        if not schema:
            return jsonify({'error': 'Could not retrieve database schema'}), 500
        # Rate limiting
        security_manager.check_rate_limit(get_client_id(), "/api/query")

        # Prompt security
        security_manager.validate_user_question(question)
        # Process user query - let LLM decide response type
        result = gemini_service.process_user_query(schema, question)
        
        if result["type"] == "error":
            return jsonify({'error': result["content"]}), 500
            
        elif result["type"] == "conversation":
            return jsonify({
                'type': 'conversation',
                'message': result["content"],
                'question': question
            })
            
        elif result["type"] == "sql" and result["needs_execution"]:
            # Execute the SQL query
            sql_query = result["content"]
            security_manager.validate_generated_sql(sql_query)
            results, error = mysql_service.execute_query(sql_query)
            
            if error:
                return jsonify({
                    'error': error,
                    'generated_sql': sql_query,
                    'type': 'sql_error'
                }), 400
            
            # Generate natural language explanation
            results_json = json.dumps(results, indent=2, default=str)
            explanation = gemini_service.explain_query_result(question, sql_query, results_json)
            
            return jsonify({
                'type': 'sql_result',
                'question': question,
                'generated_sql': sql_query,
                'results': results,
                'explanation': explanation,
                'results_count': len(results) if results else 0
            })
        else:
            return jsonify({'error': 'Unexpected response type'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tables')
def get_tables():
    """Get list of tables with sample data"""
    if not mysql_service:
        return jsonify({'error': 'MySQL service not available'}), 500
    
    try:
        # Use SQLAlchemy inspector (same as in get_database_schema)
        from sqlalchemy import inspect
        inspector = inspect(mysql_service.engine)
        security_manager.check_rate_limit(get_client_id(), "/api/tables")
        table_names = inspector.get_table_names()
        
        table_info = []
        
        for table_name in table_names:
            # Get table comment
            table_comment = inspector.get_table_comment(table_name)['text']
            
            # Get sample data using your existing method
            sample_data = mysql_service.get_sample_data(table_name, 3)
            
            table_info.append({
                'name': table_name,
                'comment': table_comment or '',  # Handle None comments
                'sample_data': sample_data,
                'sample_count': len(sample_data)
            })
        
        return jsonify({'tables': table_info})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/execute-sql', methods=['POST'])
def execute_direct_sql():
    """Execute direct SQL query (for testing)"""
    if not mysql_service:
        return jsonify({'error': 'MySQL service not available'}), 500
    
    try:
        data = request.get_json()
        sql_query = data.get('sql', '').strip()
        
        if not sql_query:
            return jsonify({'error': 'SQL query is required'}), 400
        
        # Security check: Only allow SELECT queries
        if not sql_query.upper().strip().startswith('SELECT'):
            return jsonify({'error': 'Only SELECT queries are allowed for security reasons'}), 400
        security_manager.check_rate_limit(get_client_id(), "/api/execute-sql")
        security_manager.validate_generated_sql(sql_query)
        results, error = mysql_service.execute_query(sql_query)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'results': results,
            'results_count': len(results) if results else 0
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    mysql_ok = mysql_service.test_connection() if mysql_service else False
    gemini_ok = gemini_service is not None
    
    return jsonify({
        'mysql_connected': mysql_ok,
        'gemini_available': gemini_ok,
        'database': Config.MYSQL_DATABASE,
        'read_only': True
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)