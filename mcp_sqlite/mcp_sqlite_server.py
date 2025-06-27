import sqlite3
import json
import os
import inspect
from mcp.server.fastmcp import FastMCP
import argparse
import datetime

# Constants
ALLOWED_EXTENSIONS = ['.db']
MAX_FILENAME_LENGTH = 255
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8190
DEFAULT_LOG_LEVEL = "DEBUG"
MAX_QUERY_LENGTH = 5000  # 5KB limit for queries

# Parse command line arguments for database directory
parser = argparse.ArgumentParser(description="MCP SQLite Server")
parser.add_argument('--database-dir', type=str, help='Directory to store SQLite database files')
parser.add_argument('--enable-query-logging', action='store_true', help='Enable query logging to logs/{db_name}.log')
args, unknown = parser.parse_known_args()

# Simplify the DATABASE_DIR logic to:
DATABASE_DIR = args.database_dir or os.environ.get("DATABASE_DIR") or os.path.dirname(__file__)

# Simplify the DEFAULT_DB_NAME logic to:
DEFAULT_DB_NAME = os.environ.get("DEFAULT_DATABASE", "")

# Ensure DATABASE_DIR exists
os.makedirs(DATABASE_DIR, exist_ok=True)

# Get default database name
DEFAULT_DB_PATH = os.path.join(DATABASE_DIR, DEFAULT_DB_NAME) if DEFAULT_DB_NAME else ""

print(f"DATABASE_DIR: {DATABASE_DIR}")
print(f"DEFAULT_DB_NAME: {DEFAULT_DB_NAME}")

mcp = FastMCP("mcp-sqlite-manager", port=DEFAULT_PORT, host=DEFAULT_HOST, debug=True, log_level=DEFAULT_LOG_LEVEL)

# Set up logs directory
LOGS_DIR = os.path.join(os.path.dirname(__file__), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

QUERY_LOGGING_ENABLED = args.enable_query_logging

def log_query(db_name, tool, query, result=None, error=None):
    if not QUERY_LOGGING_ENABLED:
        return
    log_path = os.path.join(LOGS_DIR, f"{db_name}.log")
    entry = {
        "timestamp": datetime.datetime.utcnow().isoformat() + 'Z',
        "db_name": db_name,
        "tool": tool,
        "query": query,
        "result": result if error is None else None,
        "error": error
    }
    try:
        with open(log_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    except Exception as e:
        print(f"Failed to write query log: {e}")

def get_connection(db_path: str = ""):
    if not db_path:
        if DEFAULT_DB_PATH:
            db_path = DEFAULT_DB_PATH
        else:
            raise ValueError("No database path provided and no default set.")
    return sqlite3.connect(db_path)

def safe_db_path(db_name: str) -> str:
    # Enhanced validation
    if not db_name or len(db_name) > MAX_FILENAME_LENGTH:
        raise ValueError(f"Invalid database name length. Must be 1-{MAX_FILENAME_LENGTH} characters.")
    if not db_name.endswith('.db') or '/' in db_name or '\\' in db_name:
        raise ValueError("Invalid database file name. Must end with .db and contain no path separators.")
    full_path = os.path.join(DATABASE_DIR, db_name)
    print(f"Using database path: {full_path}")
    return full_path

@mcp.tool()
def list_database_files() -> dict:
    """List all SQLite database files in the configured database directory."""
    try:
        print(f"Listing files in directory: {DATABASE_DIR}")
        if not os.path.exists(DATABASE_DIR):
            return {"error": f"Database directory '{DATABASE_DIR}' does not exist."}
        files = [f for f in os.listdir(DATABASE_DIR) if f.endswith('.db') and os.path.isfile(os.path.join(DATABASE_DIR, f))]
        return {"databases": files, "directory": DATABASE_DIR}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def create_database_file(db_name: str) -> dict:
    """Create a new SQLite database file in the configured directory."""
    try:
        db_path = safe_db_path(db_name)
        if os.path.exists(db_path):
            return {"error": f"Database file '{db_name}' already exists."}
        sqlite3.connect(db_path).close()
        return {"message": f"Database '{db_name}' created successfully at {db_path}."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_database_file(db_name: str) -> dict:
    """Delete a SQLite database file from the configured directory."""
    try:
        db_path = safe_db_path(db_name)
        if not os.path.exists(db_path):
            return {"error": f"Database file '{db_name}' does not exist."}
        os.remove(db_path)
        return {"message": f"Database '{db_name}' deleted successfully."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def rename_database_file(old_name: str, new_name: str) -> dict:
    """Rename a SQLite database file within the configured directory."""
    try:
        old_path = safe_db_path(old_name)
        new_path = safe_db_path(new_name)
        if not os.path.exists(old_path):
            return {"error": f"Database file '{old_name}' does not exist."}
        if os.path.exists(new_path):
            return {"error": f"Database file '{new_name}' already exists."}
        os.rename(old_path, new_path)
        return {"message": f"Database '{old_name}' renamed to '{new_name}'."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def read_query(query: str, db_name: str) -> dict:
    """Execute a SELECT query on the SQLite database."""
    try:
        if not isinstance(query, str):
            error = "Query must be a string."
            log_query(db_name, "read_query", query, error=error)
            return {"error": error}
        if len(query) > MAX_QUERY_LENGTH:
            error = f"Query too long. Maximum length is {MAX_QUERY_LENGTH} characters."
            log_query(db_name, "read_query", query, error=error)
            return {"error": error}
        if not query.strip().lower().startswith("select"):
            error = "Only SELECT queries are allowed in read_query."
            log_query(db_name, "read_query", query, error=error)
            return {"error": error}
        db_path = safe_db_path(db_name)
        with get_connection(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            rows = [dict(row) for row in cursor.fetchall()]
            log_query(db_name, "read_query", query, result="success")
            return {"rows": rows}
    except ValueError as e:
        log_query(db_name, "read_query", query, error=str(e))
        return {"error": f"Invalid input: {str(e)}"}
    except sqlite3.Error as e:
        log_query(db_name, "read_query", query, error=str(e))
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        log_query(db_name, "read_query", query, error=str(e))
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def write_query(query: str, db_name: str) -> dict:
    """Execute an INSERT, UPDATE, or DELETE query on the SQLite database."""
    try:
        if not isinstance(query, str):
            error = "Query must be a string."
            log_query(db_name, "write_query", query, error=error)
            return {"error": error}
        if len(query) > MAX_QUERY_LENGTH:
            error = f"Query too long. Maximum length is {MAX_QUERY_LENGTH} characters."
            log_query(db_name, "write_query", query, error=error)
            return {"error": error}
        if not any(query.strip().lower().startswith(cmd) for cmd in ["insert", "update", "delete"]):
            error = "Only INSERT, UPDATE, or DELETE queries are allowed in write_query."
            log_query(db_name, "write_query", query, error=error)
            return {"error": error}
        db_path = safe_db_path(db_name)
        with get_connection(db_path) as conn:
            cursor = conn.execute(query)
            conn.commit()
            log_query(db_name, "write_query", query, result=f"rows_affected: {cursor.rowcount}")
            return {"message": "Query executed successfully.", "rows_affected": cursor.rowcount}
    except ValueError as e:
        log_query(db_name, "write_query", query, error=str(e))
        return {"error": f"Invalid input: {str(e)}"}
    except sqlite3.Error as e:
        log_query(db_name, "write_query", query, error=str(e))
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        log_query(db_name, "write_query", query, error=str(e))
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def create_table(table_sql: str, db_name: str) -> dict:
    """Create a new table in the SQLite database using raw SQL."""
    try:
        if not isinstance(table_sql, str):
            error = "Query must be a string."
            log_query(db_name, "create_table", table_sql, error=error)
            return {"error": error}
        if len(table_sql) > MAX_QUERY_LENGTH:
            error = f"Query too long. Maximum length is {MAX_QUERY_LENGTH} characters."
            log_query(db_name, "create_table", table_sql, error=error)
            return {"error": error}
        if not table_sql.strip().lower().startswith("create table"):
            error = "Only CREATE TABLE statements are allowed in create_table."
            log_query(db_name, "create_table", table_sql, error=error)
            return {"error": error}
        db_path = safe_db_path(db_name)
        with get_connection(db_path) as conn:
            conn.execute(table_sql)
            conn.commit()
            log_query(db_name, "create_table", table_sql, result="success")
            return {"message": "Table created successfully."}
    except ValueError as e:
        log_query(db_name, "create_table", table_sql, error=str(e))
        return {"error": f"Invalid input: {str(e)}"}
    except sqlite3.Error as e:
        log_query(db_name, "create_table", table_sql, error=str(e))
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        log_query(db_name, "create_table", table_sql, error=str(e))
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def list_tables(db_name: str) -> dict:
    """List all tables, views, virtual tables, indexes, and other objects in the SQLite database, including their names, types, and SQL definitions."""
    try:
        db_path = safe_db_path(db_name)
        with get_connection(db_path) as conn:
            cursor = conn.execute("SELECT name, type, sql FROM sqlite_master;")
            return {"objects": [{"name": row[0], "type": row[1], "sql": row[2]} for row in cursor.fetchall()]}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def describe_table(table_name: str, db_name: str) -> dict:
    """Get the schema information for a specific table."""
    try:
        if not isinstance(table_name, str) or not table_name.isidentifier():
            return {"error": f"Invalid table name: {table_name}"}
        db_path = safe_db_path(db_name)
        with get_connection(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"PRAGMA table_info({table_name});")
            return {"schema": [dict(row) for row in cursor.fetchall()]}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def health_check() -> dict:
    """Return server health status."""
    return {"status": "ok"}

@mcp.tool()
def get_docs() -> dict:
    """Return documentation for all registered tools."""
    docs = {}
    for name, func in mcp.tools.items():
        docs[name] = inspect.getdoc(func)
    return {"tools": docs}

@mcp.tool()
def read_query_paginated(query: str, limit: int, offset: int, db_name: str) -> dict:
    """Execute a paginated SELECT query on the SQLite database."""
    try:
        if not isinstance(query, str):
            error = "Query must be a string."
            log_query(db_name, "read_query_paginated", query, error=error)
            return {"error": error}
        if len(query) > MAX_QUERY_LENGTH:
            error = f"Query too long. Maximum length is {MAX_QUERY_LENGTH} characters."
            log_query(db_name, "read_query_paginated", query, error=error)
            return {"error": error}
        if not query.strip().lower().startswith("select"):
            error = "Only SELECT queries are allowed in read_query_paginated."
            log_query(db_name, "read_query_paginated", query, error=error)
            return {"error": error}
        if not isinstance(limit, int) or limit <= 0:
            error = "Limit must be a positive integer."
            log_query(db_name, "read_query_paginated", query, error=error)
            return {"error": error}
        if not isinstance(offset, int) or offset < 0:
            error = "Offset must be a non-negative integer."
            log_query(db_name, "read_query_paginated", query, error=error)
            return {"error": error}
        db_path = safe_db_path(db_name)
        paginated_query = f"{query.strip()} LIMIT ? OFFSET ?"
        with get_connection(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(paginated_query, (limit, offset))
            rows = [dict(row) for row in cursor.fetchall()]
            log_query(db_name, "read_query_paginated", query, result="success")
            return {"rows": rows}
    except ValueError as e:
        log_query(db_name, "read_query_paginated", query, error=str(e))
        return {"error": f"Invalid input: {str(e)}"}
    except sqlite3.Error as e:
        log_query(db_name, "read_query_paginated", query, error=str(e))
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        log_query(db_name, "read_query_paginated", query, error=str(e))
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def row_count(query: str, db_name: str) -> dict:
    """Return the number of rows matching a SELECT query or in a table."""
    try:
        if not isinstance(query, str):
            error = "Query must be a string."
            log_query(db_name, "row_count", query, error=error)
            return {"error": error}
        if len(query) > MAX_QUERY_LENGTH:
            error = f"Query too long. Maximum length is {MAX_QUERY_LENGTH} characters."
            log_query(db_name, "row_count", query, error=error)
            return {"error": error}
        if not query.strip().lower().startswith("select"):
            error = "Only SELECT queries are allowed in row_count. For table row count, use 'SELECT * FROM table_name'."
            log_query(db_name, "row_count", query, error=error)
            return {"error": error}
        db_path = safe_db_path(db_name)
        count_query = f"SELECT COUNT(*) as count FROM ({query.strip()})"
        with get_connection(db_path) as conn:
            cursor = conn.execute(count_query)
            result = cursor.fetchone()
            log_query(db_name, "row_count", query, result=f"count: {result[0] if result else 0}")
            return {"count": result[0] if result else 0}
    except ValueError as e:
        log_query(db_name, "row_count", query, error=str(e))
        return {"error": f"Invalid input: {str(e)}"}
    except sqlite3.Error as e:
        log_query(db_name, "row_count", query, error=str(e))
        return {"error": f"Database error: {str(e)}"}
    except Exception as e:
        log_query(db_name, "row_count", query, error=str(e))
        return {"error": f"Unexpected error: {str(e)}"}

@mcp.tool()
def table_exists(table_name: str, db_name: str) -> dict:
    """Check if a table exists in the specified SQLite database."""
    try:
        if not isinstance(table_name, str) or not table_name.isidentifier():
            return {"error": f"Invalid table name: {table_name}"}
        db_path = safe_db_path(db_name)
        with get_connection(db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?;",
                (table_name,)
            )
            exists = cursor.fetchone() is not None
            return {"exists": exists}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def export_schema(db_name: str) -> dict:
    """Export the schema (CREATE statements) for all tables, indexes, and views in the specified SQLite database."""
    try:
        db_path = safe_db_path(db_name)
        with get_connection(db_path) as conn:
            cursor = conn.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL AND type IN ('table', 'index', 'view');")
            schema_sql = [row[0] for row in cursor.fetchall() if row[0]]
            return {"schema_sql": schema_sql}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run(transport="sse")
