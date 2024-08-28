import logging
import json
from utils.json.base import load_json_file, dump_json_file


def load_json_file_with_logging(file_path: str) -> dict:
    """
    Loads a JSON file from the specified path and returns its content as a dictionary.
    
    Args:
        file_path (str): The path to the JSON file that needs to be loaded.
        
    Returns:
        dict: The content of the JSON file as a dictionary.
        
    Raises:
        FileNotFoundError: If the specified file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    try:
        return load_json_file(file_path)
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from file: {file_path}. Error: {e}")
        raise

def dump_json_file_with_logging(file_path: str, data: dict) -> None:
    """
    Serializes a dictionary to JSON and writes it to the specified file path.
    
    Args:
        file_path (str): The path where the JSON file will be saved.
        data (dict): The dictionary data to be serialized and saved as a JSON file.
        
    Raises:
        TypeError: If the provided data is not serializable to JSON.
    """
    try:
        dump_json_file(file_path, data)
    except TypeError as e:
        logging.error(f"Error serializing data to JSON for file: {file_path}. Error: {e}")
        raise
