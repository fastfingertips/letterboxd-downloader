import json

# -- Local Imports -- #
from utils.json.custom import load_json_file_with_logging, dump_json_file_with_logging
from utils.file.custom import clean_filename, is_valid_filename
from utils.file import file_exists

from constants.project import(
    SETTINGS_FILE_NAME,
    DEFAULT_EXPORT_KEY,
    DEFAULT_LOG_KEY
)

from constants.terminal import(
    ICON_INPUT,
    ICON_INFO,
    ICON_ERROR
)   

# -- SETTINGS --

def createSettings() -> None:
    """
    Creates the settings file.
    """
    while True:
        print(f'{ICON_ERROR}The settings file could not be found. Please enter the required information.')

        logDirName = input(f'{ICON_INPUT}Log directory Name: ').strip()
        exportDirName = input(f'{ICON_INPUT}Export directory Name: ').strip()

        if not is_valid_filename(logDirName):
            logDirName = clean_filename(logDirName)
            print(f'{ICON_INFO}Log directory name cleaned: "{logDirName}"')

        if not is_valid_filename(exportDirName):
            exportDirName = clean_filename(exportDirName)
            print(f'{ICON_INFO}Export directory name cleaned: "{exportDirName}"')

        userAgree = input(f'{ICON_INPUT}Do you agree with the information you entered? (y/n): ')

        if userAgree.lower() == 'n': continue
        elif userAgree.lower() == 'y': 

            default_settings = {
                DEFAULT_LOG_KEY: logDirName,
                DEFAULT_EXPORT_KEY: exportDirName
            }

            dump_json_file_with_logging(SETTINGS_FILE_NAME, default_settings)
            break
        else:
            print(f'{ICON_ERROR}Invalid input. Please try again.')
            exit()

def readSettings() -> dict:
    """
    Reads the settings file and returns the data.
    """
    if file_exists(SETTINGS_FILE_NAME):
        # If the file exists
        try:
            # If the file is not empty, it will return the file.
            return load_json_file_with_logging(SETTINGS_FILE_NAME)
        except json.decoder.JSONDecodeError: pass

    createSettings()
    return readSettings()