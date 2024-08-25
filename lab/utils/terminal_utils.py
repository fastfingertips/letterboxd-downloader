import sys
import os
from constants.project import PRE_LOG_ERR

def set_terminal_title(title: str) -> None:
    """
    Sets the title of the terminal window.

    Args:
        title (str): The title to set for the terminal window.
    """
    os.system(f'title {title}')

def execute_terminal_command(command: str) -> None:
    """
    Executes a command in the terminal.

    Args:
        command (str): The command to execute in the terminal.
    """
    os.system(command)

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