import json

def loadJsonFile(_filePath) -> dict:
    """
    Loads a JSON file and returns its content as a dictionary.
    """
    with open(_filePath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data

def dumpJsonFile(_filePath, _data) -> None:
    """
    Dumps a dictionary to a JSON file.
    """
    with open(_filePath, 'w', encoding='utf-8') as json_file:
        json.dump(_data, json_file, indent=2)
