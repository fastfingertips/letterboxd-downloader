import os

from utils.color.custom import blink_text
from utils.time.custom import get_run_time

from constants.terminal import ICON_INFO


def ensure_directories_exist(dirs: list) -> None:
    """
    Checks if the specified directories exist. Creates them if they do not exist.

    Args:
        dirs (list): List of directory paths to check or create.
    """
    for directory in dirs:
        if directory:
            if os.path.exists(directory):
                print(f'{ICON_INFO}Directory checked: {blink_text(directory, "yellow")}')
            else:
                os.makedirs(directory)
                print(f'{ICON_INFO}Directory created: {blink_text(directory, "yellow")}')

def ensure_files_exist(files: list) -> None:
    """
    Checks if the specified files exist. Creates them if they do not exist.

    Args:
        files (list): List of file paths to check or create.
    """
    for file in files:
        if file:
            if os.path.exists(file): 
                print(f'{ICON_INFO}File checked: {blink_text(file, "yellow")}')
            else:
                with open(file, 'w') as f:
                    if file.endswith('.json'): 
                        print(f'{ICON_INFO}JSON file created: {blink_text(file, "yellow")}')
                        f.write('{}')
                    elif file.endswith('.csv'): 
                        print(f'{ICON_INFO}CSV file created: {blink_text(file, "yellow")}')
                    else:
                        f.write('')

def rename_file_with_timestamp(old_name: str, new_name: str) -> bool:
    """
    Renames a file by appending the current timestamp to the new name.

    Args:
        old_name (str): The current name of the file.
        new_name (str): The new name for the file.

    Returns:
        bool: True if the file was renamed successfully, False if a file with the new name already exists.
    """
    current_time = get_run_time()
    new_name = f'{new_name}'.replace('.', f'{current_time}.')
    if os.path.exists(new_name):
        return False
    os.rename(old_name, new_name)
    return True

def is_valid_filename(filename: str, invalid_chars: str = "\"|%:/,.\\[]<>*?") -> bool:
    """
    Checks if a filename is valid by ensuring it does not contain invalid characters.

    Args:
        filename (str): The name of the file to check.
        invalid_chars (str): A string containing invalid characters.

    Returns:
        bool: True if the filename does not contain invalid characters, False otherwise.
    """
    return all(char not in invalid_chars for char in filename)

def clean_filename(filename: str, invalid_chars: str = "\"|%:/,.\\[]<>*?") -> str:
    """
    Removes invalid characters from a filename.

    Args:
        filename (str): The name of the file to clean.
        invalid_chars (str): A string containing invalid characters to remove.

    Returns:
        str: The cleaned filename.
    """
    for char in invalid_chars:
        filename = filename.replace(char, "")
    return filename