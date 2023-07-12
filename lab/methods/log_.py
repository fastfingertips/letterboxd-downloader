from inspect import currentframe #: PMI
from .color_ import preCmdErr, preCmdInfo
from .time_ import getLogTime
from .file_ import fileExists, loadJsonFile
from .set_ import readSettings
import os
from constants.project import (SETTINGS_FILE_NAME, SESSIONS_FILE_NAME, PRE_LOG_ERR, PRE_LOG_INFO,
                               DEFAULT_LOG_KEY, SESSION_DICT_KEY, SESSION_LAST_KEY)

current_pid = str(os.getpid())

# -- LOGS --

def getLogFilePath():
    if fileExists(SETTINGS_FILE_NAME):
        settingDict = readSettings()
        logDirName = settingDict[DEFAULT_LOG_KEY]
        if checkLogDir():
            sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
            lastKey = sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_LAST_KEY]
            log_path = f'{logDirName}/{lastKey}.txt'
            return log_path

def errorLine(e): #: Error Code generator
    cl = currentframe()
    txtLog(f'{PRE_LOG_ERR} Error on line {cl.f_back.f_lineno} Exception Message: {e}')

def txtLog(r_message): #: None: Kullanıcı log lokasyonunu belirtmese de olur.
    with open(getLogFilePath(), 'a') as logFile:
        logFile.write(f'{r_message}\n')

def startLog(app_id):
    if checkLogDir():
        # If the log file exists, it is checked.
        logDir = readSettings()[DEFAULT_LOG_KEY]
        logFullPath = f'{logDir}/{app_id}.txt'
        print(f'{preCmdInfo}Session log file creating...', end=' ')
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
                print(f'{preCmdErr}Log file could not be created. Error Message: {e}')
                return False

def getCurrentSessionLogPath(app_id):
    if checkLogDir():
        logDir = readSettings()[DEFAULT_LOG_KEY]
        logFullPath = f'{logDir}/{app_id}.txt'
        if checkLogFile(logFullPath): return logFullPath
        else: return False

def checkLogFile(log_path):
    log_type = '.txt'
    if log_path.endswith(log_type):
        if os.path.exists(log_path): return True
    else: return False

def checkLogDir():
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