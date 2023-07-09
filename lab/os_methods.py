import os, sys, json
from constants import *
from color_methods import cmdBlink, preCmdInfo, preCmdErr, preCmdInput
from log_methods import txtLog, errorLine

def terminalTitle(title): #: Terminal başlığını değiştirir.
    os.system(f'title {title}')

def clearTerminal(): #: Terminali temizler.
    os.system('cls')

def terminalEcho(msg): #: Terminalde mesaj yazdırır.
    os.system(f'echo {msg}')

def dirCheck(dirs): # List
    for dir in dirs:
        if dir:
            if os.path.exists(dir): 
                pass
                # txtLog(f'{PRE_LOG_INFO}{dir} folder already exists.', logFilePath)
            else: 
                os.makedirs(dir)
                # txtLog(f'{PRE_LOG_INFO}{dir} folder created.', logFilePath) #: Oluşturulamaz ise bir izin hatası olabilir.
        print(f'{preCmdInfo}Directory checked: {cmdBlink(dir, "yellow")}')

def doReset(): # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e:
        errorLine(e)
        # txtLog(f'{PRE_LOG_ERR}Attempting to restart the program failed.', logFilePath)

def settingsFileSet(): #: Ayar dosyası kurulumu.
    if os.path.exists(SETTINGS_FILE_NAME):
        while True:
            try:
                with open(SETTINGS_FILE_NAME) as jsonFile:
                    jsonObject = json.load(jsonFile)
                    logDirName = jsonObject['log_dir']
                    exportDirName = jsonObject['export_dir']
                    break
            except Exception as e:
                errorLine(e)
    else:
        while True:
            try:
                print(f'{preCmdErr}The settings file could not be found. Please enter the required information.')
                logDirName = input(f'{preCmdInput}Log directory Name: ')
                exportDirName = input(f'{preCmdInput}Export directory Name: ')
                settings_dict = {'log_dir': logDirName,'export_dir': exportDirName,}
                with open(SETTINGS_FILE_NAME, 'w') as json_file:
                    json.dump(settings_dict, json_file)
                break
            except Exception as e:
                errorLine(e)
    return logDirName, exportDirName