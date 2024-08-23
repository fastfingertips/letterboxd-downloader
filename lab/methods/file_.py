import os

# -- FILE OPERATIONS --

def fileExists(_filePath) -> bool:
    """
    Checks if a file exists
    """
    if os.path.exists(_filePath): return True
    else: return False

def checkFilename(_fileName, _removestring="\"|%:/,.\\[]<>*?") -> bool:
    """
    Checks if a filename is valid
    """
    filenameChars = list(_fileName)
    for currentChar in filenameChars:
        if currentChar in _removestring:
            return False
    return True

def cleanFilename(_sourcestring,  _removestring="\"|%:/,.\\[]<>*?") -> str:
    """
    Removes invalid characters from a filename
    """
    for currentChar in _removestring:
        _sourcestring = _sourcestring.replace(currentChar, "")
    return _sourcestring