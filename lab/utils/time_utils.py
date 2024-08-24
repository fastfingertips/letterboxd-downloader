from datetime import datetime

def getRunTime() -> str:
    """
    Get the current date and time formatted as 'ddmmyyyyHHMMSS'.

    Returns:
        str: The current date and time in the format 'ddmmyyyyHHMMSS'.
    """
    try:
        return datetime.now().strftime('%d%m%Y%H%M%S')
    except Exception as e:
        raise RuntimeError("Failed to get run time") from e

def getLogTime() -> str:
    """
    Get the current date and time formatted as 'dd/mm/yyyy HH:MM:SS'.

    Returns:
        str: The current date and time in the format 'dd/mm/yyyy HH:MM:SS'.
    """
    try:
        return datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    except Exception as e:
        raise RuntimeError("Failed to get log time") from e