import json

# -- Local Imports -- #

from constants.project import(
    SETTINGS_FILE_NAME,
    DEFAULT_EXPORT_KEY,
    DEFAULT_LOG_KEY
)

from constants.terminal import(
    PRE_CMD_INPUT,
    PRE_CMD_INFO,
    PRE_CMD_ERR
)   

from utils.file_utils import(
    cleanFilename,
    checkFilename,
    fileExists
)

from utils.json_utils import(
    dumpJsonFile,
    loadJsonFile
)

# -- SETTINGS --

def createSettings() -> None:
    """
    Creates the settings file.
    """
    while True:
        print(f'{PRE_CMD_ERR}The settings file could not be found. Please enter the required information.')

        logDirName = input(f'{PRE_CMD_INPUT}Log directory Name: ').strip()
        exportDirName = input(f'{PRE_CMD_INPUT}Export directory Name: ').strip()

        if not checkFilename(logDirName):
            logDirName = cleanFilename(logDirName)
            print(f'{PRE_CMD_INFO}Log directory name cleaned: "{logDirName}"')

        if not checkFilename(exportDirName):
            exportDirName = cleanFilename(exportDirName)
            print(f'{PRE_CMD_INFO}Export directory name cleaned: "{exportDirName}"')

        userAgree = input(f'{PRE_CMD_INPUT}Do you agree with the information you entered? (y/n): ')

        if userAgree.lower() == 'n': continue
        elif userAgree.lower() == 'y': 

            default_settings = {
                DEFAULT_LOG_KEY: logDirName,
                DEFAULT_EXPORT_KEY: exportDirName
            }

            dumpJsonFile(SETTINGS_FILE_NAME, default_settings)
            break
        else:
            print(f'{PRE_CMD_ERR}Invalid input. Please try again.')
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