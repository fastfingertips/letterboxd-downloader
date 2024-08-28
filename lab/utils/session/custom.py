import logging
import json
import os

# -- Local Imports -- #
from utils.json.custom import load_json_file_with_logging, dump_json_file_with_logging
from utils.file.custom import rename_file_with_timestamp
from utils.file import file_exists

from constants.project import (
    SESSION_PROCESSES_KEY,
    SESSION_FINISHED_KEY,
    SESSIONS_FILE_NAME,
    SESSION_START_KEY,
    SESSION_DICT_KEY,
    SESSION_LAST_KEY
)

from constants.terminal import (
    ICON_INFO,
    ICON_ERROR
)

current_pid = str(os.getpid())

# -- SESSIONS --

def startSession(_hash) -> None:
    """
    This function checks whether the session file exists.
    """
    print(f'{ICON_INFO}Session file checking...', end=' ')
    if file_exists(SESSIONS_FILE_NAME):
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
        print(f'{ICON_INFO}Starting new session...', end=' ')
        newSession(_hash)
        print(f'successfully.') # add new session successfully
    except json.decoder.JSONDecodeError: 
        # if the file is broken or empty, the file will be backed up and a new one will be created.
        print(f'failed.') # add new session failed
        session_backup()
        sessionCreator(_hash)

def sessionCreator(_hash) -> None:
    """
    This function creates a new session file.
    """
    try:
        # if the file does not exist, it will create a new one.
        print(f'{ICON_INFO}New session file creating...', end=' ')
        createSession(_hash)
        print(f'successfully.')
    except:
        print(f'failed.')
        raise Exception(f'{ICON_INFO}Session file could not be created.')

def newSession(_hash) -> None:
    """
    This function creates a new session file or updates the existing one.
    """
    sessionRecords = load_json_file_with_logging(SESSIONS_FILE_NAME)
    if current_pid in sessionRecords[SESSION_DICT_KEY]:
        # if the process is already in the session file, the session is updated.
        update_session(_hash)
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
        dump_json_file_with_logging(SESSIONS_FILE_NAME, sessionRecords)

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
    dump_json_file_with_logging(SESSIONS_FILE_NAME, jsonObject)

def endSession(_hash) -> None:
    """
    This function ends the session file.
    """
    # current process is marked as finished.
    sessionRecords = load_json_file_with_logging(SESSIONS_FILE_NAME)
    sessionRecords[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY][_hash][SESSION_FINISHED_KEY] = True
    dump_json_file_with_logging(SESSIONS_FILE_NAME, sessionRecords)

def update_session(current_session: str) -> None:
    """
    Updates the session file with the current session.
    
    This function modifies the session file to set the last active session
    and adds the new session to the session processes. If the update fails,
    it logs the error and raises an exception.
    """
    try:
        session_records = load_json_file_with_logging(SESSIONS_FILE_NAME)

        if current_pid in session_records.get(SESSION_DICT_KEY, {}):
            logging.info("Updating the session file with the current session.")

            session_records[SESSION_DICT_KEY][current_pid][SESSION_LAST_KEY] = current_session
            session_records[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY] |= {
                current_session: {
                    SESSION_FINISHED_KEY: False
                }
            }

            dump_json_file_with_logging(SESSIONS_FILE_NAME, session_records)
            logging.info(f"Session file updated with the current session: {current_session}.")
        else:
            logging.warning(f"Process ID {current_pid} not found in session records.")
            raise KeyError(f"Process ID {current_pid} not found in session records.")
            
    except (KeyError, json.JSONDecodeError) as e:
        logging.error(f"Failed to update session file: {e}")
        raise RuntimeError(f"Could not update the session file for session {current_session}.") from e

def session_backup() -> None:
    """
    Backs up the current session file by renaming it with a timestamp.
    If the backup fails, a critical error is logged and an exception is raised.
    """
    try:
        logging.info(f"{ICON_INFO} Starting session file backup...")
        rename_file_with_timestamp(SESSIONS_FILE_NAME, f'backup_broken_{SESSIONS_FILE_NAME}')
        logging.info("Session file backup completed successfully.")
    except Exception as e:
        logging.critical(f"{ICON_ERROR} Failed to backup session file: {e}")
        raise RuntimeError("Could not backup the session file.") from e