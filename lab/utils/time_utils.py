from datetime import datetime

def get_run_time() -> str:
    """
    Retrieves the current date and time formatted as 'ddmmyyyyHHMMSS'.

    Returns:
        str: The current date and time formatted as 'ddmmyyyyHHMMSS'.

    Raises:
        RuntimeError: If there is an error formatting the date and time.
    """
    try:
        return datetime.now().strftime('%d%m%Y%H%M%S')
    except Exception as e:
        raise RuntimeError("Failed to retrieve run time.") from e

def get_log_time() -> str:
    """
    Retrieves the current date and time formatted as 'dd/mm/yyyy HH:MM:SS'.

    Returns:
        str: The current date and time formatted as 'dd/mm/yyyy HH:MM:SS'.

    Raises:
        RuntimeError: If there is an error formatting the date and time.
    """
    try:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    except Exception as e:
        raise RuntimeError("Failed to retrieve log time.") from e
