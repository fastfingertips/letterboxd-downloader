from inspect import currentframe #: PMI
import os

# -- Local Imports -- #

from utils.set.custom import readSettings
from utils.time_utils import getLogTime
from utils.file_utils import fileExists
from utils.json_utils import loadJsonFile

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
    PRE_CMD_INFO,
    PRE_CMD_ERR
)

current_pid = str(os.getpid())

# -- LOGS --

def getLogFilePath() -> str:
    """
    Returns the log file path.
    """
    if fileExists(SETTINGS_FILE_NAME):
        settingDict = readSettings()
        logDirName = settingDict[DEFAULT_LOG_KEY]
        if checkLogDir():
            sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
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

def startLog(_appId) -> bool:
    """
    Creates the log file.
    """
    if checkLogDir():
        # If the log file exists, it is checked.
        logDir = readSettings()[DEFAULT_LOG_KEY]
        logFullPath = f'{logDir}/{_appId}.txt'
        print(f'{PRE_CMD_INFO}Session log file creating...', end=' ')
        if checkLogFile(logFullPath):
            print(f'already exists.')
            return True
        else: # If the log file does not exist, it is created.
            try:
                with open(logFullPath, 'w') as logFile:
                    logFile.write(f'{PRE_LOG_INFO}Log file created. {getLogTime()}')
                print('successfully.')
                return True
            except Exception as e:
                print(f'failed.')
                print(f'{PRE_CMD_ERR}Log file could not be created. Error Message: {e}')
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
    if fileExists(SETTINGS_FILE_NAME):
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