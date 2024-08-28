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

current_pid = str(os.getpid())

def start_session(session_hash: str) -> None:
    """
    Checks whether the session file exists and starts or creates a new session accordingly.

    Parameters:
    session_hash (str): The hash identifier for the session.

    If the session file exists, a new session is added. If the file does not exist, a new session file is created.
    """
    logging.info("Checking for session file existence...")
    if file_exists(SESSIONS_FILE_NAME):
        # Session file exists; add a new session
        logging.info("Session file exists. Adding new session.")
        add_session(session_hash)
    else:
        # Session file does not exist; create a new session file
        logging.warning("Session file does not exist. Creating a new session file.")
        session_creator(session_hash)

def add_session(session_hash: str) -> None:
    """
    Adds a new session to the session file.

    If the session file is broken or empty, it will be backed up and a new one will be created.
    """
    try:
        # Attempt to start a new session
        logging.info("Starting a new session...")
        newSession(session_hash)
        logging.info("Session started successfully.")

    except json.decoder.JSONDecodeError:
        # Handle the case where the session file is broken or empty
        logging.warning("Failed to start session due to JSON decode error. Attempting to back up and create a new session.")
        session_backup()
        session_creator(session_hash)

def session_creator(session_hash: str) -> None:
    """
    Creates a new session file if it does not already exist.

    This function attempts to create a new session file using the provided
    session hash. If the session file creation fails, an error is logged
    and a RuntimeError is raised.
    """
    try:
        # Attempt to create the session file
        logging.info("Attempting to create a new session file...")
        create_session(session_hash)
        logging.info("Session file created successfully.")

    except Exception as e:
        # Log the failure and raise an exception
        logging.error(f"Failed to create session file: {e}")
        raise RuntimeError("Session file could not be created.") from e

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

def create_session(session_hash: str) -> None:
    """
    Creates a new session file with the given session hash.

    This function initializes a session file with the current process ID,
    setting up the session structure including the start, last, and process
    details. If the file creation fails, an error is logged and raised.
    """
    try:
        # Prepare the session structure
        session_data = {
            SESSION_DICT_KEY: {
                current_pid: {
                    SESSION_START_KEY: session_hash,
                    SESSION_LAST_KEY: session_hash,
                    SESSION_PROCESSES_KEY: {
                        session_hash: {
                            SESSION_FINISHED_KEY: False
                        }
                    }
                }
            }
        }

        # Dump the session data to the session file
        dump_json_file_with_logging(SESSIONS_FILE_NAME, session_data)
        logging.info(f"Session file created successfully with session hash {session_hash}.")

    except Exception as e:
        logging.error(f"Failed to create session file for hash {session_hash}: {e}")
        raise RuntimeError(f"Could not create session file with hash {session_hash}.") from e

def end_session(session_hash: str) -> None:
    """
    Marks the current process session as finished in the session file.
    
    This function updates the session record for the current process, marking
    the specified session as finished. If the session or process is not found,
    an error is logged and raised.
    """
    try:
        session_records = load_json_file_with_logging(SESSIONS_FILE_NAME)

        # Check if the current process ID exists in the session records
        if current_pid not in session_records.get(SESSION_DICT_KEY, {}):
            logging.error(f"Process ID {current_pid} not found in session records.")
            raise KeyError(f"Process ID {current_pid} not found.")

        # Check if the session hash exists for the current process
        if session_hash not in session_records[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY]:
            logging.error(f"Session {session_hash} not found for process {current_pid}.")
            raise KeyError(f"Session {session_hash} not found.")

        # Mark the session as finished
        logging.info(f"Marking session {session_hash} as finished for process {current_pid}.")
        session_records[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY][session_hash][SESSION_FINISHED_KEY] = True

        # Save the updated session records back to the file
        dump_json_file_with_logging(SESSIONS_FILE_NAME, session_records)
        logging.info(f"Session {session_hash} marked as finished successfully.")

    except (KeyError, json.JSONDecodeError) as e:
        logging.error(f"Failed to end session {session_hash}: {e}")
        raise RuntimeError(f"Could not mark session {session_hash} as finished.") from e

def update_session(session_hash: str) -> None:
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

            session_records[SESSION_DICT_KEY][current_pid][SESSION_LAST_KEY] = session_hash
            session_records[SESSION_DICT_KEY][current_pid][SESSION_PROCESSES_KEY] |= {
                session_hash: {
                    SESSION_FINISHED_KEY: False
                }
            }

            dump_json_file_with_logging(SESSIONS_FILE_NAME, session_records)
            logging.info(f"Session file updated with the current session: {session_hash}.")
        else:
            logging.warning(f"Process ID {current_pid} not found in session records.")
            raise KeyError(f"Process ID {current_pid} not found in session records.")
            
    except (KeyError, json.JSONDecodeError) as e:
        logging.error(f"Failed to update session file: {e}")
        raise RuntimeError(f"Could not update the session file for session {session_hash}.") from e

def session_backup() -> None:
    """
    Backs up the current session file by renaming it with a timestamp.
    If the backup fails, a critical error is logged and an exception is raised.
    """
    try:
        logging.info("Starting session file backup...")
        rename_file_with_timestamp(SESSIONS_FILE_NAME, f'backup_broken_{SESSIONS_FILE_NAME}')
        logging.info("Session file backup completed successfully.")
    except Exception as e:
        logging.critical(f"Failed to backup session file: {e}")
        raise RuntimeError("Could not backup the session file.") from e