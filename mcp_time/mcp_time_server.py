import datetime
import zoneinfo
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.resources import TextResource
import requests

DEFAULT_PORT = 8189
DEFAULT_HOST = "127.0.0.1"
DEFAULT_LOG_LEVEL = "DEBUG"

# Create FastMCP server instance with custom settings
mcp = FastMCP("mcp-time-manager", port=DEFAULT_PORT, host=DEFAULT_HOST, debug=True, log_level=DEFAULT_LOG_LEVEL)

@mcp.tool(name="get_current_time_in_timezone")
def get_current_time_in_timezone(timezone_name: str) -> str:
    """Get the current time in the specified timezone."""
    try:
        dt = datetime.datetime.now(zoneinfo.ZoneInfo(timezone_name))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone_name}'"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool(name="get_current_local_time")
def get_current_local_time() -> str:
    """Get the current time in the configured local timezone."""
    return f"The current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@mcp.tool(name="convert_time")
def convert_time(time_str: str, from_tz: str, to_tz: str) -> str:
    """
    Convert a time string from one timezone to another.
    If time_str is 'now', use the current time in from_tz.
    time_str format: 'YYYY-MM-DD HH:MM:SS' or 'now'
    """
    try:
        from_zone = zoneinfo.ZoneInfo(from_tz)
        to_zone = zoneinfo.ZoneInfo(to_tz)
        if time_str.lower() == "now":
            from_dt = datetime.datetime.now(from_zone)
        else:
            naive_dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            from_dt = naive_dt.replace(tzinfo=from_zone)
        to_dt = from_dt.astimezone(to_zone)
        return f"{from_dt.strftime('%Y-%m-%d %H:%M:%S')} in {from_tz} is {to_dt.strftime('%Y-%m-%d %H:%M:%S')} in {to_tz}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool(name="get_time_difference")
def get_time_difference(tz1: str, tz2: str) -> str:
    """Get the time difference in hours between two timezones."""
    try:
        now = datetime.datetime.utcnow()
        dt1 = now.replace(tzinfo=zoneinfo.ZoneInfo(tz1))
        dt2 = now.replace(tzinfo=zoneinfo.ZoneInfo(tz2))
        diff = (dt2.utcoffset() - dt1.utcoffset()).total_seconds() / 3600
        return f"Time difference between {tz1} and {tz2} is {diff} hours."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool(name="is_business_hours")
def is_business_hours(timezone: str) -> str:
    """Check if it's business hours (9am-5pm) in the given timezone."""
    try:
        now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
        if 9 <= now.hour < 17:
            return f"Yes, it is business hours in {timezone}."
        else:
            return f"No, it is not business hours in {timezone}."
    except Exception as e:
        return f"Error: {e}"

@mcp.tool(name="get_sunrise_sunset")
def get_sunrise_sunset(lat: float, lng: float, date: str = "today") -> str:
    """Get sunrise and sunset times for a location (lat, lng) and date (YYYY-MM-DD or 'today')."""
    try:
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={date}&formatted=0"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        if data['status'] == 'OK':
            sunrise = data['results']['sunrise']
            sunset = data['results']['sunset']
            return f"Sunrise: {sunrise}, Sunset: {sunset} (UTC)"
        else:
            return f"Error: {data['status']}"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool(name="get_daylight_savings_info")
def get_daylight_savings_info(timezone: str) -> str:
    """Check if daylight savings is currently in effect for a timezone."""
    try:
        now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
        is_dst = bool(now.dst())
        return f"Daylight savings is {'in effect' if is_dst else 'not in effect'} in {timezone}."
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run(transport="sse")
