# MCP SQLite Server

A lightweight, extensible server for managing and interacting with SQLite databases via the FastMCP protocol. Designed for automation, scripting, and integration, it provides a suite of tools for database file management, table operations, query execution, backup/restore, and more.

## ⚠️ Disclaimer

This tool is intended for personal projects and development use only. **Do not use in production environments.** The server runs without authentication and should only be used in trusted, local environments.

## Security Notes

- The server runs on localhost (127.0.0.1) by default – do not expose to external networks.
- No authentication is implemented.
- Database files are restricted to the configured directory to prevent path traversal.
- Only basic SQL injection protection is in place.
- **⚠️ Backup/restore functionality is now built into the server, but always maintain your own regular backups for safety.**

---

## Overview

MCP SQLite Server exposes a set of tools for working with SQLite databases, including creating, listing, and deleting database files, executing queries, managing tables, exporting schemas, backup/restore, and (optionally) logging query history. It is ideal for personal projects, hobby developers, students, and anyone who wants a simple, programmable interface to SQLite without the complexity of larger database systems.

## Features

- List, create, delete, and rename SQLite database files
- Execute SELECT, INSERT, UPDATE, and DELETE queries
- Create, list, describe, drop, and rename tables
- Check for table existence
- Paginated query support and row counting
- Export full database schema (all CREATE statements)
- Create, list, and drop indexes (including simple and custom indexes)
- Backup and restore databases to/from the built-in backups directory
- List, verify, and delete backup files
- Health check and self-documenting API
- Optional per-database query logging
- Structured error handling and input validation

## Requirements

- Python 3.7+
- MCP Python SDK
- sqlite3 (included with Python)

See `requirements.txt` for specific versions.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nmorton13/llm-tools.git
   cd mcp_sqlite
   ```
2. **(Optional) Set up a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Start the server from the `mcp_sqlite` directory:

```bash
python mcp_sqlite_server.py [--database-dir <dir>] [--enable-query-logging]
```

**Command-Line Options:**
- `--database-dir <dir>`: Directory to store SQLite database files (can be existing directory with databases or new directory) (default: current directory)
- `--enable-query-logging`: Enable per-database query logging to `logs/{db_name}.log`

The server listens on `127.0.0.1:8190` by default.

### Quick Example

```bash
# Start the server
python mcp_sqlite_server.py --database-dir ./my_databases --enable-query-logging

# The server will create the directory if it doesn't exist
# Now you can use it with Cursor AI or any MCP client
```

## Backup and Restore

The server now supports built-in backup and restore functionality. Backups are stored in the `backups/` directory inside the server folder by default. You can create, list, verify, restore, and delete backup files using the provided tools.

### Backup/Restore Example

```bash
# Create a backup of a database
# (via tool: backup_database)

# List all backups
# (via tool: list_backups)

# Verify a backup file
# (via tool: verify_backup)

# Restore a backup to a new or existing database
# (via tool: restore_database)

# Delete a backup file
# (via tool: delete_backup)
```

> **Note:** Always verify your backups and test restores to ensure data safety.

## Using with Cursor AI

You can use MCP SQLite Server as a custom MCP provider in Cursor AI. To do this, add an entry to your `~/.cursor/mcp.json` file like the following:

```json
{
  "mcpServers": {
    "sqlite": {
      "type": "custom",
      "url": "http://127.0.0.1:8190/sse",
      "description": "Local SQLite MCP server for database management"
    }
  }
}
```

After starting the server, Cursor will detect and allow you to use the SQLite tools directly from the command palette or chat.

> **Note:** This integration has not been tested with other MCP clients, but should work with any client that supports the FastMCP protocol.

## API / Tool Reference

All tools are callable via the FastMCP protocol. Key tools include:

- **list_database_files**: List all `.db` files in the configured directory
- **create_database_file**: Create a new SQLite database file
- **delete_database_file**: Delete a database file
- **rename_database_file**: Rename a database file
- **read_query**: Execute a SELECT query
- **write_query**: Execute an INSERT, UPDATE, or DELETE query
- **create_table**: Create a new table
- **list_tables**: List all tables, views, and indexes
- **describe_table**: Get schema info for a table
- **table_exists**: Check if a table exists
- **read_query_paginated**: Paginated SELECT queries
- **row_count**: Get row count for a query or table
- **export_schema**: Export all CREATE statements (schema)
- **drop_table**: Drop a table
- **rename_table**: Rename a table
- **create_index**: Create an index using raw SQL
- **create_index_simple**: Create a simple index on a single column
- **drop_index**: Drop an index
- **list_indexes**: List all indexes
- **backup_database**: Create a backup of a database (file copy or SQLite backup API)
- **restore_database**: Restore a database from a backup file
- **list_backups**: List all available backup files
- **delete_backup**: Delete a backup file
- **verify_backup**: Verify that a backup file is a valid SQLite database
- **health_check**: Server health status

## Query Logging

If `--enable-query-logging` is set, all queries are logged to `logs/{db_name}.log` as JSON lines. Each entry includes:
- Timestamp
- Database name
- Tool used
- Query
- Result or error

Example log entry:
```json
{
  "timestamp": "2024-05-30T15:00:00Z",
  "db_name": "garden.db",
  "tool": "write_query",
  "query": "DELETE FROM flowers WHERE name = 'Tulip'",
  "result": "rows_affected: 1",
  "error": null
}
```

### Sample Chat Prompts (Cursor AI Agent)

You can interact with the SQLite server using natural language in Cursor AI. Here are some example prompts:

- `Create a new SQLite database called mydata.db.`
- `Create a table named users with columns id (integer primary key) and name (text) in mydata.db.`
- `Insert a user named Alice into the users table in mydata.db.`
- `Show all users in mydata.db.`
- `How many rows are in the users table in mydata.db?`
- `Export the schema for mydata.db.`
- `Delete the database mydata.db.`
- `Show me the data in the veggies table in garden.db.`
- `Add a new column email to the users table in mydata.db.`
- `Backup the database mydata.db.`
- `Restore mydata.db from the latest backup.`
- `List all backup files.`
- `Verify the backup file mydata_backup_20240601_120000.db.`

Cursor will translate these prompts into the appropriate tool calls to the MCP SQLite Server.

## Limitations

- Single-user access only (no concurrent connections)
- No transaction management via API
- Limited to localhost access
- **Backup/restore functionality is provided, but users are still responsible for maintaining their own regular backups and verifying backup integrity.**

> **Important:** Always backup your database files before making significant changes or before updating the server software.


MIT License. See [LICENSE](../LICENSE) for details. 
