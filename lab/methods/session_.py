import json
import os

# -- Local Imports -- #

from constants.project import (
    SESSION_PROCESSES_KEY,
    SESSION_FINISHED_KEY,
    SESSIONS_FILE_NAME,
    SESSION_START_KEY,
    SESSION_DICT_KEY,
    SESSION_LAST_KEY
)

from constants.terminal import (
    PRE_CMD_INFO,
    PRE_CMD_ERR
)

from utils.file_utils import (
  fileRenamer,
  fileExists
)

from utils.json_utils import (
  loadJsonFile,
  dumpJsonFile
)

current_pid = str(os.getpid())

# -- SESSIONS --

# -- CALLS --

def startSession(_hash) -> None:
    """
    This function checks whether the session file exists.
    """
    print(f'{PRE_CMD_INFO}Session file checking...', end=' ')
    if fileExists(SESSIONS_FILE_NAME):
        # if the session file exists, the session is started.
        print(f'successfully.') # checking successfully
        addSession(_hash)
    else:
        print(f'failed.') # checking failed
        sessionCreator(_hash)

def addSession(_hash) -> None:
    """
    This function adds a new session to the session file.
    """
    try:
        # add new session
        print(f'{PRE_CMD_INFO}Starting new session...', end=' ')
        newSession(_hash)
        print(f'successfully.') # add new session successfully
    except json.decoder.JSONDecodeError: 
        # if the file is broken or empty, the file will be backed up and a new one will be created.
        print(f'failed.') # add new session failed
        sessionBackup()
        sessionCreator(_hash)

def sessionCreator(_hash) -> None:
    """
    This function creates a new session file.
    """
    try:
        # if the file does not exist, it will create a new one.
        print(f'{PRE_CMD_INFO}New session file creating...', end=' ')
        createSession(_hash)
        print(f'successfully.')
    except:
        print(f'failed.')
        raise Exception(f'{PRE_CMD_ERR}Session file could not be created.')

def newSession(_hash) -> None:
    """
    This function creates a new session file or updates the existing one.
    """
    sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
    if current_pid in sessionRecords[SESSION_DICT_KEY]:
        # if the process is already in the session file, the session is updated.
        updateSession(_hash)
    else:
        # if the process is not in the session file, a new session is created.
        sessionRecords[SESSION_DICT_KEY] |= {
            current_pid: {
                SESSION_START_KEY: _hash,
                SESSION_LAST_KEY: _hash,
                SESSION_PROCESSES_KEY: {
                    _hash: {SESSION_FINISHED_KEY: False}
                }
            }
        }
        dumpJsonFile(SESSIONS_FILE_NAME, sessionRecords)

# -- METHODS --

def createSession(_hash) -> None:
    """
    This function creates the session file.
    """
    jsonObject = {
        SESSION_DICT_KEY: {
            current_pid: {
                SESSION_START_KEY: _hash,
                SESSION_LAST_KEY: _hash,
                SESSION_PROCESSES_KEY: {
                    _hash: {
                        SESSION_FINISHED_KEY: False
                    }
                }
            }
        }
    }
    dumpJsonFile(SESSIONS_FILE_NAME, jsonObject)

def endSession(_hash) -> None:
    """
    This function ends the session file.
    """
    # current process is marked as finished.
    sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
    sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY][_hash][SESSION_FINISHED_KEY] = True
    dumpJsonFile(SESSIONS_FILE_NAME, sessionRecords)

def updateSession(_currentSession) -> None:
    """
    This function updates the session file.
    """
    sessionRecords = loadJsonFile(SESSIONS_FILE_NAME)
    sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_LAST_KEY] = _currentSession
    sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY] |= {
        _currentSession: {
            SESSION_FINISHED_KEY: False
            }
        }

    dumpJsonFile(SESSIONS_FILE_NAME, sessionRecords)

def sessionBackup() -> None:
    """
    This function backs up the last session file.
    """
    try:
        # last session file backup
        print(f'{PRE_CMD_INFO}Session file backup...', end=' ')
        fileRenamer(SESSIONS_FILE_NAME, f'backup_broken_{SESSIONS_FILE_NAME}')
        print(f'successfully.') # backup successfully
    except:
        print(f'failed.') # backup failed
        raise Exception(f'{PRE_CMD_ERR}Last session file could not be backup.')