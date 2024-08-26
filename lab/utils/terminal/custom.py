import os
import sys
from utils.terminal import execute_terminal_command
from constants.project import PRE_LOG_ERR


def restart_program() -> None:
    """
    Restarts the current program. Prompts the user for confirmation before restarting.

    If an error occurs during the restart process, it logs an error message.
    """
    try:
        execute_terminal_command('echo Press any key to reboot & pause >nul')
        execute_terminal_command('echo Confirm reboot, press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e:
        print(f'{PRE_LOG_ERR}Attempting to restart the program failed. Error Message: {e}')