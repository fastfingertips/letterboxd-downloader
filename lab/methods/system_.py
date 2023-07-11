from constants.project import PRE_LOG_ERR
import os
import sys
from .time_ import getRunTime
from .color_ import cmdBlink, preCmdInfo

# -- FILE --

def dirCheck(dirs): # List
    for dir in dirs:
        if dir:
            if os.path.exists(dir): pass
            else: os.makedirs(dir)
        print(f'{preCmdInfo}Directory checked: {cmdBlink(dir, "yellow")}')

def fileCheck(files): # List
    for file in files:
        if file:
            if os.path.exists(file): pass
            else:
                with open(file, 'w') as f:
                    if file.endswith('.json'): 
                        print(f'json file created: {file}')
                        f.write('{}')
                    elif file.endswith('.csv'): 
                        print(f'csv file created: {file}')
                    else: f.write('')
        print(f'{preCmdInfo}File checked: {cmdBlink(file, "yellow")}')

def fileRenamer(old_name, new_name) -> bool:
    current_time = getRunTime()
    new_name = f'{new_name}'.replace('.', f'{current_time}.')
    if os.path.exists(new_name): return False
    os.rename(old_name, new_name)
    return True

# -- TERMINAL --

def terminalTitle(title:str):
    os.system(f'title {title}')

def terminalSystem(s:str):
    os.system(s)

def doReset(): # Porgramı yeniden başlat
    try:
        terminalSystem('echo Press and any key to reboot & pause >nul')
        terminalSystem('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e: print(f'{PRE_LOG_ERR}Attempting to restart the program failed. Error Message: {e}')