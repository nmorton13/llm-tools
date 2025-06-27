# MCP Time Manager

A lightweight, extensible server for time and timezone-related operations via the FastMCP protocol. Designed for automation, scripting, and integration, it provides a suite of tools for time conversion, timezone queries, sunrise/sunset calculations, and more.

## ⚠️ Disclaimer

This tool is intended for personal projects and development use only. **Do not use in production environments.** The server runs without authentication and should only be used in trusted, local environments.

## Security Notes

- The server runs on localhost (127.0.0.1) by default – do not expose to external networks.
- No authentication is implemented.
- **No rate limiting or abuse protection.**

---

## Overview

MCP Time Manager exposes a set of tools for working with time and timezones, including getting the current time in any timezone, converting times between zones, checking business hours, and retrieving sunrise/sunset times using the [api.sunrise-sunset.org](https://sunrise-sunset.org/api) service.

It is ideal for personal projects, hobby developers, students, and anyone who wants a simple, programmable interface to time and timezone data.

## Features

- Get the current time in any IANA timezone
- Convert times between timezones
- Get the time difference between two timezones
- Check if it's business hours (9am-5pm) in a given timezone
- Get sunrise and sunset times for any location and date (via api.sunrise-sunset.org)
- Check if daylight savings is in effect for a timezone
- Structured error handling and input validation

## Requirements

- Python 3.9+
- MCP Python SDK
- [requests](https://pypi.org/project/requests/) (for sunrise/sunset API)

See `requirements.txt` for specific versions.

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nmorton13/llm-tools.git
   cd mcp_time
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

Start the server from the `mcp_time` directory:

```bash
python mcp_time_server.py
```

The server listens on `127.0.0.1:8189` by default.

## Using with Cursor AI or LLM Chat

You can use MCP Time Manager as a custom MCP provider in Cursor AI or interact with it via chat prompts. To add it to Cursor, add an entry to your `~/.cursor/mcp.json` file like:

```json
{
  "mcpServers": {
    "time": {
      "type": "custom",
      "url": "http://127.0.0.1:8189/sse",
      "description": "Local Time MCP server for time and timezone management"
    }
  }
}
```

After starting the server, Cursor will detect and allow you to use the time tools directly from the command palette or chat.

> **Note:** This integration has not been tested with other MCP clients, but should work with any client that supports the FastMCP protocol.

## API / Tool Reference

All tools are callable via the FastMCP protocol. Key tools include:

- **get_current_time_in_timezone**: Get the current time in any IANA timezone
- **get_current_local_time**: Get the current time in the server's local timezone
- **convert_time**: Convert a time string from one timezone to another
- **get_time_difference**: Get the time difference in hours between two timezones
- **is_business_hours**: Check if it's business hours (9am-5pm) in a given timezone
- **get_sunrise_sunset**: Get sunrise and sunset times for a location and date (uses api.sunrise-sunset.org)
- **get_daylight_savings_info**: Check if daylight savings is currently in effect for a timezone

## Example Chat Prompts (Cursor AI Agent or LLM)

You can interact with the Time Manager using natural language in Cursor AI or any LLM chat interface. Here are some example prompts:

- `What is the current time in Tokyo?`
- `Convert 2025-06-27 17:00:00 from New York time to London time.`
- `How many hours ahead is Sydney compared to Los Angeles?`
- `Is it business hours in Berlin right now?`
- `When is sunrise in Anchorage, Alaska?`
- `When is sunset in Lawrence, Kansas?`
- `Is daylight savings in effect in Paris?`
- `What time is it in Central Time currently in NYC`

Cursor or the LLM will translate these prompts into the appropriate tool calls to the MCP Time Manager server.

## Sunrise/Sunset Data

Sunrise and sunset times are retrieved using the [api.sunrise-sunset.org](https://sunrise-sunset.org/api) public API. Results are returned in UTC by default. The server adds a timeout to API requests for reliability.

## Limitations

- Single-user access only (no concurrent connections)
- No authentication or rate limiting
- Limited to localhost access
- Relies on third-party API for sunrise/sunset data (subject to their availability and rate limits)

MIT License. See [LICENSE](../LICENSE) for details. 
