import os
from constants.terminal import PRE_CMD_INFO
from utils.cmd_format import cmdBlink
from utils.time_utils import getRunTime

def dirCheck(dirs: list) -> None:
    """
    Check if a directory exists, if not create it
    """
    for dir in dirs:
        if dir:
            if os.path.exists(dir):
                print(f'{PRE_CMD_INFO}Directory checked: {cmdBlink(dir, "yellow")}')
            else:
                os.makedirs(dir)
                print(f'{PRE_CMD_INFO}Directory created: {cmdBlink(dir, "yellow")}')

def fileCheck(files: list) -> None:
    """
    Check if a file exists, if not create it
    """
    for file in files:
        if file:
            if os.path.exists(file): 
                print(f'{PRE_CMD_INFO}File checked: {cmdBlink(file, "yellow")}')
            else:
                with open(file, 'w') as f:
                    if file.endswith('.json'): 
                        print(f'{PRE_CMD_INFO}json file created: {cmdBlink(file, "yellow")}')
                        f.write('{}')
                    elif file.endswith('.csv'): 
                        print(f'{PRE_CMD_INFO}csv file created: {cmdBlink(file, "yellow")}')
                    else: f.write('')

def fileRenamer(old_name, new_name) -> bool:
    """
    Rename a file
    """
    current_time = getRunTime()
    new_name = f'{new_name}'.replace('.', f'{current_time}.')
    if os.path.exists(new_name): return False
    os.rename(old_name, new_name)
    return True

def fileExists(_filePath) -> bool:
    """
    Checks if a file exists at the given path.
    """
    return os.path.exists(_filePath)

def checkFilename(_fileName, _removestring="\"|%:/,.\\[]<>*?") -> bool:
    """
    Checks if a filename is valid by ensuring it doesn't contain invalid characters.
    """
    return all(char not in _removestring for char in _fileName)

def cleanFilename(_sourcestring, _removestring="\"|%:/,.\\[]<>*?") -> str:
    """
    Cleans a filename by removing invalid characters.
    """
    for currentChar in _removestring:
        _sourcestring = _sourcestring.replace(currentChar, "")
    return _sourcestring