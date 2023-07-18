import os
import sys

# -- Local Imports -- #

from constants.project import PRE_LOG_ERR
from .time_ import getRunTime

from .color_ import(
    preCmdInfo,
    cmdBlink
)

# -- FILE --

def dirCheck(dirs:list) -> None:
    """
    Check if a directory exists, if not create it
    """
    for dir in dirs:
        if dir:
            if os.path.exists(dir): pass
            else:
                print(f'{preCmdInfo}Directory created: {cmdBlink(dir, "yellow")}')
                os.makedirs(dir)
        print(f'{preCmdInfo}Directory checked: {cmdBlink(dir, "yellow")}')

def fileCheck(files:list) -> None:
    """
    Check if a file exists, if not create it
    """
    for file in files:
        if file:
            if os.path.exists(file): pass
            else:
                with open(file, 'w') as f:
                    if file.endswith('.json'): 
                        print(f'json file created: {file}')
                        f.write('{}')
                    elif file.endswith('.csv'): 
                        print(f'csv file created: {file}')
                    else: f.write('')
        print(f'{preCmdInfo}File checked: {cmdBlink(file, "yellow")}')

def fileRenamer(old_name, new_name) -> bool:
    """
    Rename a file
    """
    current_time = getRunTime()
    new_name = f'{new_name}'.replace('.', f'{current_time}.')
    if os.path.exists(new_name): return False
    os.rename(old_name, new_name)
    return True

# -- TERMINAL --

def terminalTitle(title:str) -> None:
    """
    Change the title of the terminal
    """
    os.system(f'title {title}')

def terminalSystem(s:str) -> None:
    """
    Execute a command in the terminal
    """
    os.system(s)

def doReset() -> None:
    """
    Restart the program
    """
    try:
        terminalSystem('echo Press and any key to reboot & pause >nul')
        terminalSystem('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e: print(f'{PRE_LOG_ERR}Attempting to restart the program failed. Error Message: {e}')