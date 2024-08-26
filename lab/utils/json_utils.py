import json
from utils.log.custom import txtLog

def load_json_file(file_path: str) -> dict:
    """
    Loads a JSON file from the specified file path and returns its content as a dictionary.
    
    Args:
        file_path (str): The path to the JSON file that needs to be loaded.
        
    Returns:
        dict: The content of the JSON file as a dictionary.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
            return data
    except FileNotFoundError:
        txtLog(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        txtLog(f"Error decoding JSON from file: {file_path}. Error: {e}")
        raise


def dump_json_file(file_path: str, data: dict) -> None:
    """
    Dumps a dictionary to a JSON file at the specified file path.
    
    Args:
        file_path (str): The path where the JSON file will be saved.
        data (dict): The dictionary data to be saved as a JSON file.
        
    Raises:
        TypeError: If the provided data is not serializable to JSON.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=2)
    except TypeError as e:
        txtLog(f"Error serializing data to JSON for file: {file_path}. Error: {e}")
        raise
