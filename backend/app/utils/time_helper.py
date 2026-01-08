import datetime

def get_current_utc_time():
    """Returns the current UTC time as an ISO 8601 formatted string."""
    return datetime.datetime.utcnow().isoformat() + 'Z'