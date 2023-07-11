SETTINGS_FILE_NAME = 'settings'+'.json' # settings file name
SPLIT_LIMIT = 1500 # split limit
PARTITION_LIMIT = 10 # partition limit
# Domain
SITE_PROTOCOL, SITE_URL = "https://", "letterboxd.com"
SITE_DOMAIN = SITE_PROTOCOL + SITE_URL # https://letterboxd.com
# Log
DEFAULT_LOG_KEY = 'log_dir' # default log dir name
DEFAULT_EXPORT_KEY = 'export_dir' # default export dir name
PRE_LOG_INFO = "Info: " # log file ingo msg pre
PRE_LOG_ERR = "Error: " # log file err msg pre  
# Cmd Lines
SUP_LINE = '_'*80 # sup line lenght
SUB_LINE = '¯'*80 # sub line lenght
CMD_PRINT_FILMS = True # Print the movies after every request?
SPLIT_PARAMETER = "split:" # split parameter
# Session
SESSION_DICT_KEY = 'sessions' # sessions key
SESSION_PROCESSES_KEY = 'processes' # session processes key
SESSION_PIDS_KEY = 'pids' # session pids key

SESSIONS_FILE_NAME = 'sessions'+'.json' # sessions file name

SESSION_PID_KEY = 'pid' # session pid key
SESSION_START_KEY = 'start_key' # session start key
SESSION_LAST_KEY = 'last_key' # session end key

SESSION_FINISHED_KEY = 'finished' # session finished key