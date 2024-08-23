# File Names
SETTINGS_FILE_NAME = 'settings.json'
SESSIONS_FILE_NAME = 'sessions.json'

# Limits
SPLIT_LIMIT = 1500
PARTITION_LIMIT = 10

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