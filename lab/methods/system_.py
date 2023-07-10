from constants.project import PRE_LOG_ERR, PRE_LOG_INFO, SETTINGS_FILE_NAME
import os
import sys
import json
from .log_ import txtLog, errorLine
from .color_ import cmdBlink, preCmdInfo, preCmdErr, preCmdInput #

def dirCheck(dirs): # List
    for dir in dirs:
        if dir:
            if os.path.exists(dir):
                txtLog(f'{PRE_LOG_INFO}{dir} folder already exists.')
            else:
                os.makedirs(dir)
                txtLog(f'{PRE_LOG_INFO}{dir} folder created.') #: Oluşturulamaz ise bir izin hatası olabilir.
        print(f'{preCmdInfo}Directory checked: {cmdBlink(dir, "yellow")}')

def fileCheck(files): # List
    for file in files:
        if file:
            if os.path.exists(file):
                txtLog(f'{PRE_LOG_INFO}{file} file already exists.')
            else:
                with open(file, 'w') as f:
                    if file.endswith('.json'): 
                        print(f'json file created: {file}')
                        f.write('{}')
                    else: f.write('')
                txtLog(f'{PRE_LOG_INFO}{file} file created.')
        print(f'{preCmdInfo}File checked: {cmdBlink(file, "yellow")}')

def terminalSystem(s:str):
    os.system(s)

def doReset(): # Porgramı yeniden başlat
    try:
        terminalSystem('echo Press and any key to reboot & pause >nul')
        terminalSystem('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e:
        errorLine(e)
        txtLog(f'{PRE_LOG_ERR}Attempting to restart the program failed.')

def settingsFileSet(): #: Ayar dosyası kurulumu.
    if os.path.exists(SETTINGS_FILE_NAME):
        while True:
            with open(SETTINGS_FILE_NAME) as jsonFile:
                jsonObject = json.load(jsonFile)
                logDirName = jsonObject['log_dir']
                exportDirName = jsonObject['export_dir']
                break
    else:
        while True:
            print(f'{preCmdErr}The settings file could not be found. Please enter the required information.')
            logDirName = input(f'{preCmdInput}Log directory Name: ')
            exportDirName = input(f'{preCmdInput}Export directory Name: ')
            settings_dict = {'log_dir': logDirName,'export_dir': exportDirName,}
            with open(SETTINGS_FILE_NAME, 'w') as json_file:
                json.dump(settings_dict, json_file)
            break
    return logDirName, exportDirName

def terminalTitle(title:str):
    os.system(f'title {title}')