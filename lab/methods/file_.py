import json
import os

# -- FILE OPERATIONS --

def loadJsonFile(_filePath):
    """
    Loads a json file
    """
    with open(_filePath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data

def dumpJsonFile(_filePath, _data):
    """
    Dumps a json file
    """
    with open(_filePath, 'w', encoding='utf-8') as json_file:
        json.dump(_data, json_file, indent=2)

def fileExists(_filePath) -> bool:
    """
    Checks if a file exists
    """
    if os.path.exists(_filePath): return True
    else: return False

def checkFilename(_fileName, _removestring="\"|%:/,.\\[]<>*?"):
    """
    Checks if a filename is valid
    """
    filenameChars = list(_fileName)
    for currentChar in filenameChars:
        if currentChar in _removestring:
            return False
    return True

def cleanFilename(_sourcestring,  _removestring="\"|%:/,.\\[]<>*?") :
    """
    Removes invalid characters from a filename
    """
    for currentChar in _removestring:
        _sourcestring = _sourcestring.replace(currentChar, "")
    return _sourcestring