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
- Get the current time in the server's local timezone
- Convert times between timezones
- Get the time difference between two timezones
- Check if it's business hours (9am-5pm) in a given timezone
- Get sunrise and sunset times for any location and date (via api.sunrise-sunset.org)
- Check if daylight savings is in effect for a timezone
- Get the Bitcoin block height for a given date/time/timezone (via blockchain.info API)
- Calculate days until (or since) a given date
- Convert a date/time in a timezone to a Unix timestamp
- Add or subtract days, hours, and minutes from the current time in a specified timezone
- Get the next occurrence of a specific weekday in a timezone
- Check if it's currently weekend in a given timezone
- Format a Unix timestamp into a readable date/time string in a specified timezone
- Get detailed time components (year, month, day, hour, minute, second, weekday, season, moon phase) for a timezone
- Calculate the duration between two date/time points in a timezone
- Get the date/time that was a specified duration ago in a timezone
- Get the current season in a given timezone
- Get the moon phase for a given date (approximate calculation)
- List common timezone names for reference
- Get the current UTC offset for a timezone
- Validate if a timezone name is valid
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

- **get_current_time_in_timezone**: Get the current time in any IANA timezone.
- **get_current_local_time**: Get the current time in the server's local timezone.
- **convert_time**: Convert a time string from one timezone to another.
- **get_time_difference**: Get the time difference in hours between two timezones.
- **is_business_hours**: Check if it's business hours (9am-5pm) in a given timezone.
- **get_sunrise_sunset**: Get sunrise and sunset times for a location and date (uses api.sunrise-sunset.org).
- **get_daylight_savings_info**: Check if daylight savings is currently in effect for a timezone.
- **get_bitcoin_block_height_for_date**: Get the Bitcoin block height for a given date/time/timezone. (Uses the blockchain.info public API)
- **days_until**: Calculates the number of days from today until a future date (YYYY-MM-DD), or how many days have passed if the date is in the past.
- **convert_to_unix_timestamp**: Converts a human-readable date and time to a Unix timestamp.
- **add_subtract_time**: Adds or subtracts a duration from the current time in a specified timezone.
- **get_next_weekday**: Get the next occurrence of a specific weekday (0=Monday, 6=Sunday) in a timezone.
- **is_weekend**: Check if it's currently weekend (Saturday or Sunday) in a given timezone.
- **format_timestamp**: Format a Unix timestamp into a readable date/time string in a specified timezone.
- **get_time_components**: Get detailed time components (year, month, day, hour, minute, second, weekday, season, moon phase) for a timezone.
- **calculate_duration**: Calculate the duration between two date/time points in a timezone.
- **get_time_ago**: Get the date/time that was a specified duration ago in a timezone.
- **get_season**: Get the current season in a given timezone.
- **get_moon_phase**: Get the moon phase for a given date (approximate calculation, not precise astronomical data).
- **list_common_timezones**: List common timezone names for reference.
- **get_timezone_offset**: Get the current UTC offset for a timezone.
- **validate_timezone**: Validate if a timezone name is valid.

## Example Chat Prompts (Cursor AI Agent or LLM)

You can interact with the Time Manager using natural language in Cursor AI or any LLM chat interface. Here are some example prompts:

- `What is the current time in Tokyo?`
- `Convert 2025-06-27 17:00:00 from New York time to London time.`
- `How many hours ahead is Sydney compared to Los Angeles?`
- `Is it business hours in Berlin right now?`
- `When is sunrise in Anchorage, Alaska?`
- `When is sunset in Lawrence, Kansas?`
- `Is daylight savings in effect in Paris?`
- `What time is it in Central Time currently in NYC?`
- `How many days until Christmas?`
- `What was the Unix timestamp for 2024-01-01 00:00:00 UTC?`
- `Add 3 days and 4 hours to the current time in London.`
- `When is the next Friday in Los Angeles?`
- `Is it the weekend in Sydney?`
- `Format the timestamp 1704067200 in Asia/Tokyo.`
- `Show all time components for Paris.`
- `How long was it between 2024-01-01 08:00:00 and 2024-01-02 10:30:00 in UTC?`
- `What time was it 2 days and 5 hours ago in Berlin?`
- `What season is it in Buenos Aires?`
- `What is the moon phase today?`
- `List some common timezone names.`
- `What is the UTC offset for America/Denver?`
- `Is 'Europe/Zurich' a valid timezone?`
- `What was the Bitcoin block height on 2021-12-11 at 1PM`

## Sunrise/Sunset, Moon Phase, and Bitcoin Block Height Data

- Sunrise and sunset times are retrieved using the [api.sunrise-sunset.org](https://sunrise-sunset.org/api) public API. Results are returned in UTC by default. The server adds a timeout to API requests for reliability.
- **Moon phase calculation is approximate and not suitable for precise astronomical purposes.**
- The `get_bitcoin_block_height_for_date` tool retrieves block height information using the [blockchain.info](https://blockchain.info/) public API. Results depend on the availability and accuracy of this third-party service.

## Limitations

- Single-user access only (no concurrent connections)
- No authentication or rate limiting
- Limited to localhost access
- Relies on third-party API for sunrise/sunset data (subject to their availability and rate limits)

MIT License. See [LICENSE](../LICENSE) for details. 
