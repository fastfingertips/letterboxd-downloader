import os
import sys

# -- Local Imports -- #

from constants.project import PRE_LOG_ERR

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