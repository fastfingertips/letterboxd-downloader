import json

def read_file(file_path: str) -> str:
    """
    Reads the content of a specified file and returns it as a string.
    
    Args:
        file_path (str): The path to the file to be read.
        
    Returns:
        str: The entire content of the file as a string.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path: str, content: str) -> None:
    """
    Writes a string to a specified file.
    
    Args:
        file_path (str): The path to the file where the content will be written.
        content (str): The string content to be written to the file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def load_json_file(file_path: str) -> dict:
    """
    Loads and parses a JSON file, returning its content as a dictionary.
    
    Args:
        file_path (str): The path to the JSON file to be loaded.
        
    Returns:
        dict: The parsed JSON data as a dictionary.
    """
    content = read_file(file_path)
    return json.loads(content)

def dump_json_file(file_path: str, data: dict) -> None:
    """
    Serializes a dictionary to a JSON string and writes it to a specified file.
    
    Args:
        file_path (str): The path to the file where the JSON data will be saved.
        data (dict): The dictionary to be serialized and saved as a JSON file.
    """
    content = json.dumps(data, indent=2)
    write_file(file_path, content)
