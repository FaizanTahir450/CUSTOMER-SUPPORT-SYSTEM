import google.generativeai as genai
from config import Config
import json
from typing import Optional, Dict, Any
from security.sql_security import SQLSecurity  # ✅ Part 2: Import SQLSecurity

class GeminiService:
    def __init__(self):
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        
        # ✅ Use free tier model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.sql_security = SQLSecurity()  # ✅ Initialize SQLSecurity

    def process_user_query(self, schema: str, question: str) -> Dict[str, Any]:
        """
        Process user query and let LLM decide whether to generate SQL or provide conversation
        Returns: {
            "type": "sql" | "conversation" | "error",
            "content": str,
            "needs_execution": bool
        }
        """
        
        prompt = f"""
You are an intelligent database assistant. Your name is SANDRA. The database is a university database. Analyze the user's question and decide the appropriate response.

Database Schema:
{schema}

User Question: {question}

IMPORTANT SECURITY RULES:
1. This is a READ-ONLY database. You can ONLY generate SELECT queries.
2. NEVER generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or any data modification queries.
3. If user asks to modify data, explain that this is a read-only system.

DECISION GUIDE:
1. If the user asks a data-related question that requires database querying, generate a VALID MySQL SELECT query ONLY.
2. If the user engages in greetings or small talk, provide a friendly conversational response.
3. If the question asks for data modification, explain this is read-only.
4. If the question is unclear or cannot be answered with the available schema, provide a helpful explanation.
5. If the user asks an irrelevant question that is not related to database or is not a small talk \ greeting politely reject the user.
6. If the user asks question in Hindi/Urdu reply in Urdu.

RESPONSE FORMAT:
- For SQL queries: Start with [SQL] followed by the MySQL SELECT query
- For conversations: Start with [CONV] followed by your response
"""
        
        try:
            response = self.model.generate_content(prompt)
            raw_response = response.text.strip()
            
            # Parse the response type
            if raw_response.startswith('[SQL]'):
                sql_query = raw_response.replace('[SQL]', '').strip()
                sql_query = self._clean_sql_response(sql_query)
                
                # ✅ Enforce SQL security
                try:
                    self.sql_security.validate(sql_query)
                except ValueError as e:
                    return {
                        "type": "conversation",
                        "content": str(e),
                        "needs_execution": False,
                        "message": "Blocked unsafe SQL"
                    }

                return {
                    "type": "sql",
                    "content": sql_query,
                    "needs_execution": True,
                    "message": "SQL query generated successfully"
                }
                
            elif raw_response.startswith('[CONV]'):
                conversation_response = raw_response.replace('[CONV]', '').strip()
                return {
                    "type": "conversation", 
                    "content": conversation_response,
                    "needs_execution": False,
                    "message": "Conversational response"
                }
                
            else:
                # If no marker, try to auto-detect SQL
                if self._looks_like_sql(raw_response) and self._is_read_only_query(raw_response):
                    cleaned_sql = self._clean_sql_response(raw_response)
                    
                    # ✅ Enforce SQL security even in fallback
                    try:
                        self.sql_security.validate(cleaned_sql)
                    except ValueError as e:
                        return {
                            "type": "conversation",
                            "content": str(e),
                            "needs_execution": False,
                            "message": "Blocked unsafe SQL"
                        }

                    return {
                        "type": "sql",
                        "content": cleaned_sql,
                        "needs_execution": True,
                        "message": "SQL query detected and cleaned"
                    }
                else:
                    return {
                        "type": "conversation",
                        "content": raw_response,
                        "needs_execution": False,
                        "message": "Conversational response (auto-detected)"
                    }
            
        except Exception as e:
            return {
                "type": "error",
                "content": f"Error processing query: {str(e)}",
                "needs_execution": False,
                "message": "Processing error"
            }

    def _is_read_only_query(self, query: str) -> bool:
        """Security check: Ensure query is read-only (SELECT only)"""
        if not query:
            return False
            
        query_upper = query.upper().strip()
        
        forbidden_operations = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 
            'CREATE', 'TRUNCATE', 'REPLACE', 'MERGE', 'LOCK',
            'UNLOCK', 'GRANT', 'REVOKE'
        ]
        
        is_select = query_upper.startswith('SELECT') or query_upper.startswith('WITH')
        has_forbidden = any(op in query_upper for op in forbidden_operations)
        
        return is_select and not has_forbidden

    def _looks_like_sql(self, text: str) -> bool:
        """Check if text looks like SQL (fallback detection)"""
        if not text:
            return False
            
        text_upper = text.upper().strip()
        sql_indicators = [
            text_upper.startswith('SELECT '),
            text_upper.startswith('WITH '),
            ' FROM ' in text_upper,
            ' WHERE ' in text_upper,
            ' JOIN ' in text_upper,
            ' GROUP BY ' in text_upper,
            ' ORDER BY ' in text_upper
        ]
        
        return any(sql_indicators)

    def _clean_sql_response(self, sql_query: str) -> str:
        """Clean SQL response from markdown and other artifacts"""
        if not sql_query:
            return ""
            
        cleaned = sql_query.strip()
        if cleaned.startswith('```sql'):
            cleaned = cleaned[6:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
            
        cleaned = cleaned.strip()
        if cleaned.endswith(';'):
            cleaned = cleaned[:-1].strip()
            
        return cleaned

    def explain_query_result(self, original_question: str, sql_query: str, query_results: Any) -> str:
        """Explain query results in natural language"""
        if isinstance(query_results, (list, dict)):
            results_str = json.dumps(query_results, indent=2, default=str)
        else:
            results_str = str(query_results)
        
        prompt = f"""
Original question: {original_question}
SQL query used: {sql_query}
Query results: {results_str}

Provide a clear, simple explanation of these results for a non-technical user.
Keep it concise and focused on what the data means in relation to the original question.
"""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Could not generate explanation: {e}"

# --------------------------------------------
# ✅ MAIN FUNCTION FOR TESTING
# --------------------------------------------
if __name__ == "__main__":
    print("🔍 Testing GeminiService...")

    try:
        gemini = GeminiService()
        print("✅ GeminiService initialized successfully.")

        # Sample test
        sample_schema = """
        Table: students
        Columns:
          - id INT NOT NULL
          - name VARCHAR(255)
          - age INT
          - department VARCHAR(255)
        """

        sample_question = "Get the names of students older than 20."

        print("\n🧠 Generating SQL for sample question...")
        result = gemini.process_user_query(sample_schema, sample_question)
        print("\nGenerated Result:")
        print(f"Type: {result['type']}")
        print(f"Content: {result['content']}")
        print(f"Needs Execution: {result['needs_execution']}")

    except Exception as e:
        print("❌ Error testing GeminiService:")
        print(e)
