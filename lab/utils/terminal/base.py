import os


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