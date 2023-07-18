from .file_ import fileExists, loadJsonFile, dumpJsonFile, checkFilename, cleanFilename
from .color_ import preCmdErr, preCmdInput, preCmdInfo
from constants.project import SETTINGS_FILE_NAME, DEFAULT_LOG_KEY, DEFAULT_EXPORT_KEY
import json

# -- SETTINGS --

def createSettings() -> None:
    """
    Creates the settings file.
    """
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

def readSettings() -> dict:
    """
    Reads the settings file and returns the data.
    """
    if fileExists(SETTINGS_FILE_NAME):
        # If the file exists
        try:
            # If the file is not empty, it will return the file.
            return loadJsonFile(SETTINGS_FILE_NAME)
        except json.decoder.JSONDecodeError: pass

    createSettings()
    return readSettings()