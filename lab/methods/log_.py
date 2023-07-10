from inspect import currentframe #: PMI
from constants.project import SETTINGS_FILE_NAME, PRE_LOG_ERR, SESSIONS_FILE_NAME
from .time_ import getLogTime
import json
import os

def startSession():
    if not os.path.exists(SESSIONS_FILE_NAME):
        with open(SESSIONS_FILE_NAME, 'w') as jsonFile:
            jsonObject = {'sessions': {}}
            json.dump(jsonObject, jsonFile, indent=4)
    elif os.path.exists(SESSIONS_FILE_NAME):
        with open(SESSIONS_FILE_NAME) as jsonFile:
            try: # If the file is empty, it will be filled with an empty dictionary.
                json.load(jsonFile)
            except json.decoder.JSONDecodeError: # If the file is empty, it will be filled with an empty dictionary.
                jsonObject = {'sessions': {}}
                with open(SESSIONS_FILE_NAME, 'w') as jsonFile:
                    json.dump(jsonObject, jsonFile, indent=4)
    else: pass # If the file exists, it will not be created.

def findLastLogFile():
    if os.path.exists(SETTINGS_FILE_NAME):
        with open(SETTINGS_FILE_NAME) as jsonFile:
            jsonObject = json.load(jsonFile)
            logDirName = jsonObject['log_dir']
            with open(SESSIONS_FILE_NAME) as jsonFile:
                jsonObject = json.load(jsonFile)
                sessionKeys = jsonObject['sessions'].keys()
                return f'{logDirName}/{list(sessionKeys)[-1]}.txt'

def errorLine(e): #: Error Code generator
    cl = currentframe()
    txtLog(f'{PRE_LOG_ERR} Error on line {cl.f_back.f_lineno} Exception Message: {e}')

def txtLog(r_message): #: None: Kullanıcı log lokasyonunu belirtmese de olur.
        with open(findLastLogFile(), "a", encoding="utf-8") as f: #: Eklemek üzere bir dosya açar, mevcut değilse dosyayı oluşturur
            f.writelines(f'{getLogTime()} {r_message}\n')

