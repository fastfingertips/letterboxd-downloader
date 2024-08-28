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
        if checkLogDir():
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
    if checkLogDir():
        log_dir = readSettings()[DEFAULT_LOG_KEY]
        log_full_path = os.path.join(log_dir, f'{app_id}.txt')
        
        logging.info("Checking if log file exists...")
        
        if checkLogFile(log_full_path):
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

def getCurrentSessionLogPath(_appId) -> str:
    """
    Returns the current session log file path.
    """
    if checkLogDir():
        logDir = readSettings()[DEFAULT_LOG_KEY]
        logFullPath = f'{logDir}/{_appId}.txt'
        if checkLogFile(logFullPath): return logFullPath
        else: return False

def checkLogFile(_logPath) -> bool:
    """
    Checks if the log file exists.
    """
    logType = '.txt'
    if _logPath.endswith(logType):
        if os.path.exists(_logPath): return True
    else: return False

def checkLogDir() -> bool:
    """
    Checks if the log directory exists.
    """
    if file_exists(SETTINGS_FILE_NAME):
        settingDict = readSettings()
        logDirName = settingDict[DEFAULT_LOG_KEY]

        if os.path.exists(logDirName): return True
        else:
            try:
                os.makedirs(logDirName)
                return True
            except Exception as e:
                return False
    else: return False