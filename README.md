# llm-tools
**Welcome!**

This is a collection of small tools that are, hopefully, growing, which I’ve built and found handy when working with agents. These tools are designed to work with the Model Context Protocol (MCP), so they can be used by AI models, automation scripts, or anyone who finds them useful.

---

## What’s Here?

### 1. `mcp_sqlite`

A lightweight SQLite server that exposes database management and query features as MCP tools.

- **Location:** [mcp_sqlite](./mcp_sqlite)
- **Features:**
  - Create, delete, and manage SQLite databases
  - Run queries and export schemas
  - All features are accessible as MCP tools (see the subfolder README for details)

---

### 2. `mcp_time`

A simple time-utility server.

- **Location:** [mcp_time](./mcp_time)
- **Features:**
  - Returns the current time in the server’s local timezone (handy for bots or automations)

---

## Getting Started

1. **Clone the repository:**
   ```sh
   git clone https://github.com/nmorton13/llm-tools.git
   cd llm-tools
   ```

2. **See each tool’s folder or script for setup and usage instructions.**

3. **Install dependencies as needed:**
   ```sh
   pip install -r requirements.txt
   ```

---

## License

See the [LICENSE](./LICENSE) file for details.
