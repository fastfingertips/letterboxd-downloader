import json
import os

def loadJsonFile(filePath):
    with open(filePath, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
        return data

def dumpJsonFile(filePath, data):
    with open(filePath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)

# -- FILE OPERATIONS --

def fileExists(f) -> bool:
    if os.path.exists(f): return True
    else: return False

def checkFilename(filename, removestring="\"|%:/,.\\[]<>*?"):
    filenameChars = list(filename)
    for currentChar in filenameChars:
        if currentChar in removestring:
            return False
    return True

def cleanFilename(sourcestring,  removestring="\"|%:/,.\\[]<>*?") :
    for currentChar in removestring:
        sourcestring = sourcestring.replace(currentChar, "")
    return sourcestring