from inspect import currentframe #: PMI
from .color_ import preCmdErr, preCmdInput, preCmdInfo
from .time_ import getLogTime
from .system_ import fileRenamer
import json
import os
from constants.project import (SETTINGS_FILE_NAME, SESSIONS_FILE_NAME,
                               PRE_LOG_ERR, PRE_LOG_INFO,
                               DEFAULT_LOG_KEY, DEFAULT_EXPORT_KEY,
                               SESSION_DICT_KEY, SESSION_PROCESSES_KEY,
                               SESSION_START_KEY,SESSION_LAST_KEY,
                               SESSION_FINISHED_KEY)

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

# -- SESSIONS --

def createSession(app_id) -> None:
    # If the session file does not exist, it is created.
    jsonObject = {
        SESSION_DICT_KEY: {
            current_pid: {
                SESSION_START_KEY: app_id,
                SESSION_LAST_KEY: app_id,
                SESSION_PROCESSES_KEY: {
                    app_id: {
                        SESSION_FINISHED_KEY: False
                    }
                }
            }
        }
    }
    dumpJsonFile(SESSIONS_FILE_NAME, jsonObject)

def endSession(current_hash) -> None:
    # Current process is marked as finished.
    sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
    sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY][current_hash][SESSION_FINISHED_KEY] = True
    dumpJsonFile(SESSIONS_FILE_NAME, sessionRecords)

def newSession(start_hash) -> None:
    sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
    if current_pid in sessionRecords[SESSION_DICT_KEY]:
        # If the process is already in the session file, the session is updated.
        updateSession(start_hash)
    else:
        # If the process is not in the session file, a new session is created.
        sessionRecords[SESSION_DICT_KEY] |= {
            current_pid: {
                SESSION_START_KEY: start_hash,
                SESSION_LAST_KEY: start_hash,
                SESSION_PROCESSES_KEY: {
                    start_hash: {SESSION_FINISHED_KEY: False}
                }
            }
        }
        dumpJsonFile(SESSIONS_FILE_NAME, sessionRecords)

def updateSession(current_session):
    sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
    sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_LAST_KEY] = current_session
    sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY] |= {
        current_session: {
            SESSION_FINISHED_KEY: False
            }
        }

    dumpJsonFile(SESSIONS_FILE_NAME, sessionRecords)

def sessionCreator(app_id):
    try:
        # If the file does not exist, it will create a new one.
        print(f'{preCmdInfo}New session file creating...', end=' ')
        createSession(app_id)
        print(f'successfully.')
    except:
        print(f'failed.')
        raise Exception(f'{preCmdErr}Session file could not be created.')

def sessionBackup():
    try:
        # last session file backup
        print(f'{preCmdInfo}Session file backup...', end=' ')
        fileRenamer(SESSIONS_FILE_NAME, f'backup_broken_{SESSIONS_FILE_NAME}')
        print(f'successfully.') # backup successfully
    except:
        print(f'failed.') # backup failed
        raise Exception(f'{preCmdErr}Last session file could not be backup.')

def addSession(start_hash):
    try:
        # add new session
        print(f'{preCmdInfo}Starting new session...', end=' ')
        newSession(start_hash)
        print(f'successfully.') # add new session successfully
    except json.decoder.JSONDecodeError: 
        # If the file is broken or empty, the file will be backed up and a new one will be created.
        print(f'failed.') # add new session failed
        sessionBackup()
        sessionCreator(start_hash)

def startSession(start_hash) -> None:
    print(f'{preCmdInfo}Session file checking...', end=' ')
    if fileExists(SESSIONS_FILE_NAME):
        # If the session file exists, the session is started.
        print(f'successfully.') # checking successfully
        addSession(start_hash)
    else:
        print(f'failed.') # checking failed
        sessionCreator(start_hash)

# -- SETTINGS --

def createSettings():
    while True:
        print(f'{preCmdErr}The settings file could not be found. Please enter the required information.')

        logDirName = input(f'{preCmdInput}Log directory Name: ').strip()
        exportDirName = input(f'{preCmdInput}Export directory Name: ').strip()

        if not checkFilename(logDirName):
            logDirName = cleanFilename(logDirName)
            print(f'{preCmdInfo}Log directory name cleaned: "{logDirName}"')

        if not checkFilename(exportDirName):
            exportDirName = cleanFilename(exportDirName)
            print(f'{preCmdInfo}Export directory name cleaned: "{exportDirName}"')

        userAgree = input(f'{preCmdInput}Do you agree with the information you entered? (y/n): ')

        if userAgree.lower() == 'n': continue
        elif userAgree.lower() == 'y': 

            default_settings = {
                DEFAULT_LOG_KEY: logDirName,
                DEFAULT_EXPORT_KEY: exportDirName
            }
            
            dumpJsonFile(SETTINGS_FILE_NAME, default_settings)
            break
        else:
            print(f'{preCmdErr}Invalid input. Please try again.')
            exit()

def readSettings():
    if fileExists(SETTINGS_FILE_NAME):
        # If the file exists
        try:
            # If the file is not empty, it will return the file.
            return loadJsonFile(SETTINGS_FILE_NAME)
        except json.decoder.JSONDecodeError: pass

    createSettings()
    return readSettings()

def loadJsonFile(filePath):
    with open(filePath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data

def dumpJsonFile(filePath, data):
    with open(filePath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)

# -- FILE OPERATIONS --

def fileExists(f) -> bool:
    if os.path.exists(f): return True
    else: return False

def checkFilename(filename, removestring="\"|%:/,.\\[]<>*?"):
    filenameChars = list(filename)
    for currentChar in filenameChars:
        if currentChar in removestring:
            return False
    return True

def cleanFilename(sourcestring,  removestring="\"|%:/,.\\[]<>*?") :
    for currentChar in removestring:
        sourcestring = sourcestring.replace(currentChar, "")
    return sourcestring