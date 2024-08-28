import logging
from inspect import currentframe #: PMI
import os

# -- Local Imports -- #

from utils.json.custom import load_json_file_with_logging
from utils.time.custom import get_log_time
from utils.set.custom import readSettings
from utils.file import file_exists

from constants.project import(
    SETTINGS_FILE_NAME,
    SESSIONS_FILE_NAME,
    SESSION_DICT_KEY,
    SESSION_LAST_KEY,
    DEFAULT_LOG_KEY,
    PRE_LOG_INFO,
    PRE_LOG_ERR
)

from constants.terminal import(
    ICON_INFO,
    ICON_ERROR
)

current_pid = str(os.getpid())

def setup_logging():
    """
    Set up the logging configuration.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log'),
            # logging.StreamHandler()
        ]
    )

def getLogFilePath() -> str:
    """
    Returns the log file path.
    """
    if file_exists(SETTINGS_FILE_NAME):
        settingDict = readSettings()
        logDirName = settingDict[DEFAULT_LOG_KEY]
        if check_log_dir():
            sessionRecords = load_json_file_with_logging(SESSIONS_FILE_NAME)
            lastKey = sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_LAST_KEY]
            log_path = f'{logDirName}/{lastKey}.txt'
            return log_path

def errorLine(_e) -> None:
    """
    Writes the error line with the error message to the log file.
    """
    cl = currentframe()
    txtLog(f'{PRE_LOG_ERR} Error on line {cl.f_back.f_lineno} Exception Message: {_e}')

def txtLog(_message) -> None:
    """
    Writes the message to the log file.
    """
    with open(getLogFilePath(), 'a') as logFile:
        logFile.write(f'{_message}\n')

def start_log(app_id: str) -> bool:
    """
    Creates a log file for the specified application ID if it does not already exist.

    Parameters:
    app_id (str): The identifier for the application. This will be used to name the log file.

    Returns:
    bool: True if the log file was successfully created or already exists, False otherwise.
    """
    if check_log_dir():
        log_dir = readSettings()[DEFAULT_LOG_KEY]
        log_full_path = os.path.join(log_dir, f'{app_id}.txt')
        
        logging.info("Checking if log file exists...")
        
        if check_log_file(log_full_path):
            logging.info("Log file already exists.")
            return True
        
        try:
            with open(log_full_path, 'w') as log_file:
                log_file.write(f'{PRE_LOG_INFO}Log file created. {get_log_time()}')
            logging.info("Log file created successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to create log file. Error: {e}")
            return False

def get_current_session_log_path(app_id: str) -> str:
    """
    Returns the path of the current session log file if it exists.

    Parameters:
    app_id (str): The identifier for the application. This will be used to name the log file.

    Returns:
    str: The path to the log file if it exists.
    None: If the log file does not exist.
    """
    if check_log_dir():
        log_dir = readSettings()[DEFAULT_LOG_KEY]
        log_full_path = os.path.join(log_dir, f'{app_id}.txt')
        
        if check_log_file(log_full_path):
            return log_full_path
        else:
            logging.warning(f"Log file {log_full_path} does not exist.")
            return None
    else:
        logging.error("Log directory does not exist.")
        return None

def check_log_file(log_path: str) -> bool:
    """
    Checks if a log file exists at the specified path and has a '.txt' extension.

    Parameters:
    log_path (str): The path to the log file to check.

    Returns:
    bool: True if the log file exists and ends with '.txt', False otherwise.
    """
    if not os.path.exists(log_path):
        logging.error(f"Log file '{log_path}' does not exist.")
        return False
    
    if not log_path.endswith('.txt'):
        logging.warning(f"Log file '{log_path}' does not have a '.txt' extension.")
        return False
    
    return True

def check_log_dir() -> bool:
    """
    Checks if the log directory exists and creates it if it doesn't.

    Returns:
    bool: True if the log directory exists or was successfully created, False otherwise.
    """
    if file_exists(SETTINGS_FILE_NAME):
        try:
            settings_dict = readSettings()
            log_dir_name = settings_dict[DEFAULT_LOG_KEY]

            if os.path.exists(log_dir_name):
                logging.info(f"Log directory '{log_dir_name}' already exists.")
                return True
            else:
                os.makedirs(log_dir_name)
                logging.info(f"Log directory '{log_dir_name}' created successfully.")
                return True
        except Exception as e:
            logging.error(f"Failed to create log directory '{log_dir_name}'. Error: {e}")
            return False
    else:
        logging.error(f"Settings file '{SETTINGS_FILE_NAME}' does not exist.")
        return False