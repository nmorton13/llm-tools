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

# --- Existing Tools (with minor improvements) ---

@mcp.tool(name="get_current_time_in_timezone")
def get_current_time_in_timezone(timezone_name: str) -> str:
    """Get the current time in the specified timezone."""
    try:
        dt = datetime.datetime.now(zoneinfo.ZoneInfo(timezone_name))
        return dt.strftime('%Y-%m-%d %H:%M:%S %Z')
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone_name}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

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
        return (f"{from_dt.strftime('%Y-%m-%d %H:%M:%S')} in {from_tz} is "
                f"{to_dt.strftime('%Y-%m-%d %H:%M:%S')} in {to_tz}")
    except zoneinfo.ZoneInfoNotFoundError as e:
        return f"Error: Unknown timezone provided: {e}"
    except ValueError:
        return f"Error: Invalid time format for '{time_str}'. Please use 'YYYY-MM-DD HH:MM:SS'."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_time_difference")
def get_time_difference(tz1: str, tz2: str) -> str:
    """Get the time difference in hours between two timezones."""
    try:
        now = datetime.datetime.utcnow()
        dt1 = now.replace(tzinfo=zoneinfo.ZoneInfo(tz1))
        dt2 = now.replace(tzinfo=zoneinfo.ZoneInfo(tz2))
        diff = (dt2.utcoffset() - dt1.utcoffset()).total_seconds() / 3600
        return f"Time difference between {tz1} and {tz2} is {diff} hours."
    except zoneinfo.ZoneInfoNotFoundError as e:
        return f"Error: Unknown timezone provided: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="is_business_hours")
def is_business_hours(timezone: str) -> str:
    """Check if it's business hours (9am-5pm, Mon-Fri) in the given timezone."""
    try:
        now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
        # Monday is 0 and Sunday is 6
        if 9 <= now.hour < 17 and now.weekday() < 5:
            return f"Yes, it is currently business hours in {timezone}."
        else:
            return f"No, it is not currently business hours in {timezone}."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_sunrise_sunset")
def get_sunrise_sunset(lat: float, lng: float, date: str = "today") -> str:
    """Get sunrise and sunset times for a location (lat, lng) and date (YYYY-MM-DD or 'today')."""
    try:
        url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={lng}&date={date}&formatted=0"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data['status'] == 'OK':
            sunrise = data['results']['sunrise']
            sunset = data['results']['sunset']
            return f"Sunrise: {sunrise}, Sunset: {sunset} (Times are in UTC)"
        else:
            return f"Error from API: {data.get('status', 'Unknown error')}"
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the sunrise-sunset API. {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_daylight_savings_info")
def get_daylight_savings_info(timezone: str) -> str:
    """Check if daylight savings is currently in effect for a timezone."""
    try:
        now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
        is_dst = bool(now.dst())
        return f"Daylight savings is {'in effect' if is_dst else 'not in effect'} in {timezone}."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- NEW TOOL ---

@mcp.tool(name="get_bitcoin_block_height_for_date")
def get_bitcoin_block_height_for_date(date_str: str, time_str: str = "00:00:00", timezone: str = "UTC") -> str:
    """
    Gets the approximate Bitcoin block height for a given date and time.
    :param date_str: The date in 'YYYY-MM-DD' format.
    :param time_str: The time in 'HH:MM:SS' format. Defaults to the start of the day.
    :param timezone: The timezone for the provided date and time (e.g., 'America/New_York'). Defaults to UTC.
    """
    try:
        dt_naive = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        tz = zoneinfo.ZoneInfo(timezone)
        dt_aware = dt_naive.replace(tzinfo=tz)
        timestamp = int(dt_aware.timestamp())
        url = f"https://blockchain.info/blocks/{timestamp}000?format=json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        blocks = response.json()
        # Find the first block with .time <= timestamp
        block = next((b for b in blocks if b.get('time', 0) <= timestamp), None)
        if block:
            block_height = block.get('height')
            block_time_unix = block.get('time')
            block_time_utc = datetime.datetime.fromtimestamp(block_time_unix, tz=datetime.timezone.utc)
            return (f"The first block on or before {date_str} {time_str} {timezone} "
                    f"was block #{block_height}, mined at {block_time_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}.")
        else:
            return "No block found for that timestamp."
    except (ValueError, TypeError):
        return "Error: Invalid date, time, or timezone format. Please use 'YYYY-MM-DD' and 'HH:MM:SS'."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except requests.exceptions.RequestException as e:
        return f"Error: Could not connect to the Bitcoin API. {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

# --- ADDITIONAL TOOLS ---

@mcp.tool(name="days_until")
def days_until(date_str: str) -> str:
    """Calculates the number of days from today until a future date (YYYY-MM-DD)."""
    try:
        target_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        delta = target_date - today
        if delta.days < 0:
            return f"{abs(delta.days)} days have passed since {date_str}."
        else:
            return f"There are {delta.days} days until {date_str}."
    except ValueError:
        return "Error: Invalid date format. Please use 'YYYY-MM-DD'."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="convert_to_unix_timestamp")
def convert_to_unix_timestamp(date_str: str, time_str: str, timezone: str) -> str:
    """Converts a human-readable date and time to a Unix timestamp."""
    try:
        dt_naive = datetime.datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt_aware = dt_naive.replace(tzinfo=zoneinfo.ZoneInfo(timezone))
        timestamp = int(dt_aware.timestamp())
        return f"Unix timestamp for {date_str} {time_str} {timezone} is: {timestamp}"
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except ValueError:
        return "Error: Invalid date or time format. Please use 'YYYY-MM-DD' and 'HH:MM:SS'."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="add_subtract_time")
def add_subtract_time(
    timezone: str, 
    days: int = 0, 
    hours: int = 0, 
    minutes: int = 0
) -> str:
    """Adds or subtracts a duration from the current time in a specified timezone."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        current_time = datetime.datetime.now(tz)
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        new_time = current_time + delta
        return f"The new time will be {new_time.strftime('%Y-%m-%d %H:%M:%S %Z')}."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_next_weekday")
def get_next_weekday(target_weekday: int, timezone: str = "UTC") -> str:
    """Get the next occurrence of a specific weekday (0=Monday, 6=Sunday)."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        today = datetime.datetime.now(tz)
        days_ahead = target_weekday - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_date = today + datetime.timedelta(days=days_ahead)
        return f"The next {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][target_weekday]} in {timezone} is {next_date.strftime('%Y-%m-%d')}."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="is_weekend")
def is_weekend(timezone: str) -> str:
    """Check if it's currently weekend in the given timezone."""
    try:
        now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
        if now.weekday() >= 5:
            return f"Yes, it is currently weekend in {timezone}."
        else:
            return f"No, it is not currently weekend in {timezone}."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="format_timestamp")
def format_timestamp(timestamp: int, timezone: str = "UTC", format_str: str = "%Y-%m-%d %H:%M:%S %Z") -> str:
    """Format a Unix timestamp into a readable date/time string."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        dt = datetime.datetime.fromtimestamp(timestamp, tz=tz)
        return dt.strftime(format_str)
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_time_components")
def get_time_components(timezone: str) -> str:
    """Get detailed time components (year, month, day, hour, minute, second, weekday, season, moon phase) for a timezone."""
    try:
        now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # Determine season
        month = now.month
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"
        # Determine moon phase (same logic as get_moon_phase)
        target_date = now.date()
        days_since_new_moon = (target_date - datetime.date(2000, 1, 6)).days % 29.53
        if days_since_new_moon < 3.69:
            moon_phase = "New Moon"
        elif days_since_new_moon < 7.38:
            moon_phase = "Waxing Crescent"
        elif days_since_new_moon < 11.07:
            moon_phase = "First Quarter"
        elif days_since_new_moon < 14.76:
            moon_phase = "Waxing Gibbous"
        elif days_since_new_moon < 18.45:
            moon_phase = "Full Moon"
        elif days_since_new_moon < 22.14:
            moon_phase = "Waning Gibbous"
        elif days_since_new_moon < 25.83:
            moon_phase = "Last Quarter"
        else:
            moon_phase = "Waning Crescent"
        return (
            f"Current time in {timezone}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
            f"Year: {now.year}, Month: {now.month}, Day: {now.day}\n"
            f"Hour: {now.hour}, Minute: {now.minute}, Second: {now.second}\n"
            f"Weekday: {weekday_names[now.weekday()]}\n"
            f"Season: {season}\n"
            f"Moon phase: {moon_phase}"
        )
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="calculate_duration")
def calculate_duration(start_date: str, start_time: str, end_date: str, end_time: str, timezone: str) -> str:
    """Calculate the duration between two date/time points."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        start_dt = datetime.datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        end_dt = datetime.datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        duration = end_dt - start_dt
        total_seconds = int(duration.total_seconds())
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"Duration: {days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except ValueError:
        return "Error: Invalid date/time format. Use 'YYYY-MM-DD' and 'HH:MM:SS'."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_time_ago")
def get_time_ago(days: int = 0, hours: int = 0, minutes: int = 0, timezone: str = "UTC") -> str:
    """Get the date/time that was a specified duration ago."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.datetime.now(tz)
        delta = datetime.timedelta(days=days, hours=hours, minutes=minutes)
        past_time = now - delta
        return f"{days} days, {hours} hours, {minutes} minutes ago in {timezone} was: {past_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_season")
def get_season(timezone: str) -> str:
    """Get the current season in the given timezone."""
    try:
        now = datetime.datetime.now(zoneinfo.ZoneInfo(timezone))
        month = now.month
        if month in [12, 1, 2]:
            season = "Winter"
        elif month in [3, 4, 5]:
            season = "Spring"
        elif month in [6, 7, 8]:
            season = "Summer"
        else:
            season = "Autumn"
        return f"It is currently {season} in {timezone}."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="get_moon_phase")
def get_moon_phase(date: str = "today") -> str:
    """Get the moon phase for a given date (uses a simple approximation)."""
    try:
        if date.lower() == "today":
            target_date = datetime.date.today()
        else:
            target_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        days_since_new_moon = (target_date - datetime.date(2000, 1, 6)).days % 29.53
        if days_since_new_moon < 3.69:
            phase = "New Moon"
        elif days_since_new_moon < 7.38:
            phase = "Waxing Crescent"
        elif days_since_new_moon < 11.07:
            phase = "First Quarter"
        elif days_since_new_moon < 14.76:
            phase = "Waxing Gibbous"
        elif days_since_new_moon < 18.45:
            phase = "Full Moon"
        elif days_since_new_moon < 22.14:
            phase = "Waning Gibbous"
        elif days_since_new_moon < 25.83:
            phase = "Last Quarter"
        else:
            phase = "Waning Crescent"
        return f"Moon phase on {target_date.strftime('%Y-%m-%d')}: {phase}"
    except ValueError:
        return "Error: Invalid date format. Please use 'YYYY-MM-DD' or 'today'."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="list_common_timezones")
def list_common_timezones() -> str:
    """List common timezone names for reference."""
    common_tz = [
        "UTC", "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
        "Europe/London", "Europe/Paris", "Europe/Berlin", "Asia/Tokyo", "Asia/Shanghai",
        "Australia/Sydney", "Pacific/Auckland", "America/Sao_Paulo", "Africa/Cairo"
    ]
    return "Common timezone names:\n" + "\n".join(common_tz)

@mcp.tool(name="get_timezone_offset")
def get_timezone_offset(timezone: str) -> str:
    """Get the current UTC offset for a timezone."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
        now = datetime.datetime.now(tz)
        offset = now.utcoffset()
        offset_hours = int(offset.total_seconds() / 3600)
        offset_minutes = int((offset.total_seconds() % 3600) / 60)
        sign = "+" if offset_hours >= 0 else ""
        return f"Current UTC offset for {timezone}: {sign}{offset_hours:02d}:{offset_minutes:02d}"
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Error: Unknown timezone '{timezone}'"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

@mcp.tool(name="validate_timezone")
def validate_timezone(timezone: str) -> str:
    """Validate if a timezone name is valid."""
    try:
        zoneinfo.ZoneInfo(timezone)
        return f"'{timezone}' is a valid timezone."
    except zoneinfo.ZoneInfoNotFoundError:
        return f"'{timezone}' is not a valid timezone."
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    mcp.run(transport="sse")
