"""
Constants for the project configuration.

These constants are used throughout the project for setting file names,
managing limits, defining the site domain, and configuring logging behavior.
"""

# File Names
SETTINGS_FILE_NAME = 'settings.json'  # The name of the settings file used to store configuration data.
SESSIONS_FILE_NAME = 'sessions.json'  # The name of the file where session data is stored.

# Limits
SPLIT_LIMIT = 1500  # The maximum size before splitting data into smaller parts.
PARTITION_LIMIT = 10  # The maximum number of partitions allowed.

# Domain
SITE_PROTOCOL = "https://"
SITE_URL = "letterboxd.com"
SITE_DOMAIN = SITE_PROTOCOL + SITE_URL

# Logging
DEFAULT_LOG_KEY = 'log_dir'  # Default log directory name
DEFAULT_EXPORT_KEY = 'export_dir'  # Default export directory name
PRE_LOG_INFO = "Info: "  # Prefix for log information messages
PRE_LOG_ERR = "Error: "  # Prefix for log error messages

# Command Lines
SUP_LINE = '_' * 80  # Upper line length
SUB_LINE = '¯' * 80  # Lower line length
CMD_PRINT_FILMS = True  # Print the movies after every request?
SPLIT_PARAMETER = "split:"

# Session Keys
SESSION_DICT_KEY = 'sessions'
SESSION_PROCESSES_KEY = 'processes' 
SESSION_PIDS_KEY = 'pids' 
SESSION_PID_KEY = 'pid'
SESSION_START_KEY = 'start_key'
SESSION_LAST_KEY = 'last_key'
SESSION_FINISHED_KEY = 'finished'