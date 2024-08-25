import os
from constants.terminal import PRE_CMD_INFO
from utils.cmd_format import cmd_blink
from utils.time_utils import get_run_time

def dirCheck(dirs: list) -> None:
    """
    Check if a directory exists, if not create it
    """
    for dir in dirs:
        if dir:
            if os.path.exists(dir):
                print(f'{PRE_CMD_INFO}Directory checked: {cmd_blink(dir, "yellow")}')
            else:
                os.makedirs(dir)
                print(f'{PRE_CMD_INFO}Directory created: {cmd_blink(dir, "yellow")}')

def fileCheck(files: list) -> None:
    """
    Check if a file exists, if not create it
    """
    for file in files:
        if file:
            if os.path.exists(file): 
                print(f'{PRE_CMD_INFO}File checked: {cmd_blink(file, "yellow")}')
            else:
                with open(file, 'w') as f:
                    if file.endswith('.json'): 
                        print(f'{PRE_CMD_INFO}json file created: {cmd_blink(file, "yellow")}')
                        f.write('{}')
                    elif file.endswith('.csv'): 
                        print(f'{PRE_CMD_INFO}csv file created: {cmd_blink(file, "yellow")}')
                    else: f.write('')

def fileRenamer(old_name, new_name) -> bool:
    """
    Rename a file
    """
    current_time = get_run_time()
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