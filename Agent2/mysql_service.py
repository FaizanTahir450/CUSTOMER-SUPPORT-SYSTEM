from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from config import Config
from security.sql_security import SQLSecurity  


class MySQLService:
    def __init__(self):
        self.connection_string = (
            f"mysql+mysqlconnector://"
            f"{Config.MYSQL_USER}:{Config.MYSQL_PASSWORD}"
            f"@{Config.MYSQL_HOST}:{Config.MYSQL_PORT}"
            f"/{Config.MYSQL_DATABASE}"
        )
        self.engine = None
        self.Session = None
        self.connect()
        self.sql_security = SQLSecurity()  # ✅ Initialize SQLSecurity

    def connect(self):
        """Establish connection to MySQL database using SQLAlchemy"""
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,
                echo=False,
                pool_recycle=3600,
            )
            self.Session = sessionmaker(bind=self.engine)
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Connected to MySQL database successfully using SQLAlchemy")
        except SQLAlchemyError as e:
            print(f"Error connecting to MySQL: {e}")
            raise

    def get_connection(self):
        """Get database connection"""
        return self.engine.connect()

    def get_database_schema(self) -> str:
        """Get schema information for all tables in the database"""
        try:
            inspector = inspect(self.engine)
            schema_info = []

            for table_name in inspector.get_table_names():
                table_comment = inspector.get_table_comment(table_name)['text']
                columns = inspector.get_columns(table_name)

                table_schema = f"Table: {table_name}"
                if table_comment:
                    table_schema += f" (Comment: {table_comment})"
                table_schema += "\nColumns:\n"

                for col in columns:
                    col_def = f"  - {col['name']} {col['type']}"
                    if not col['nullable']:
                        col_def += " NOT NULL"
                    if col['default'] is not None:
                        col_def += f" DEFAULT {col['default']}"
                    if col.get('comment'):
                        col_def += f" COMMENT '{col['comment']}'"
                    table_schema += col_def + "\n"

                foreign_keys = inspector.get_foreign_keys(table_name)
                if foreign_keys:
                    table_schema += "Foreign Keys:\n"
                    for fk in foreign_keys:
                        col_names = ', '.join(fk['constrained_columns'])
                        ref_table = fk['referred_table']
                        ref_cols = ', '.join(fk['referred_columns'])
                        table_schema += f"  - {col_names} → {ref_table}({ref_cols})\n"

                schema_info.append(table_schema)

            return "\n\n".join(schema_info)

        except SQLAlchemyError as e:
            print(f"Error getting database schema: {e}")
            return ""

    def execute_query(self, query: str) -> Tuple[Optional[List[Dict]], Optional[str]]:
        """Execute a SQL query with SQLSecurity check"""
        try:
            # ✅ Enforce SQL security before execution
            self.sql_security.validate(query)

            with self.engine.connect() as conn:
                result = conn.execute(text(query))

                try:
                    columns = result.keys()
                    rows = result.fetchall()
                    formatted_results = [dict(zip(columns, row)) for row in rows]
                    return formatted_results, None
                except:
                    affected_rows = result.rowcount
                    return [{"affected_rows": affected_rows}], None

        except SQLAlchemyError as e:
            error_msg = f"SQLAlchemy Error: {e}"
            print(error_msg)
            return None, error_msg
        except ValueError as ve:
            # Blocked by SQLSecurity
            return None, str(ve)

    def execute_transaction(self, queries: List[str]) -> Tuple[bool, Optional[str]]:
        """Execute multiple queries in a transaction"""
        try:
            with self.engine.begin() as conn:
                for query in queries:
                    # ✅ Enforce SQL security for each query
                    self.sql_security.validate(query)
                    conn.execute(text(query))
            return True, None
        except SQLAlchemyError as e:
            return False, str(e)
        except ValueError as ve:
            return False, str(ve)

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict]:
        """Get sample data from a table"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT {limit}"))
                columns = result.keys()
                rows = result.fetchall()
                return [dict(zip(columns, row)) for row in rows]
        except SQLAlchemyError as e:
            print(f"Error getting sample data: {e}")
            return []

    def get_dataframe(self, query: str, **kwargs) -> pd.DataFrame:
        """Execute query and return results as pandas DataFrame"""
        try:
            self.sql_security.validate(query)
            return pd.read_sql(query, self.engine, **kwargs)
        except SQLAlchemyError as e:
            print(f"Error getting DataFrame: {e}")
            return pd.DataFrame()
        except ValueError as ve:
            print(f"SQLSecurity blocked query: {ve}")
            return pd.DataFrame()

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database"""
        try:
            inspector = inspect(self.engine)
            return table_name in inspector.get_table_names()
        except SQLAlchemyError as e:
            print(f"Error checking table existence: {e}")
            return False

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError:
            return False

    def close(self):
        """Close database connection pool"""
        if self.engine:
            self.engine.dispose()


if __name__ == "__main__":
    print("🔍 Testing MySQL connection...")

    try:
        db = MySQLService()

        if db.test_connection():
            print("✅ MySQLService is working correctly.")
        else:
            print("⚠️ MySQLService could not establish a connection.")

    except Exception as e:
        print("❌ Fatal error while initializing MySQLService:")
        print(e)
