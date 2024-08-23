import os
from methods.color_ import preCmdInfo, cmdBlink
from methods.time_ import getRunTime

def dirCheck(dirs: list) -> None:
    """
    Check if a directory exists, if not create it
    """
    for dir in dirs:
        if dir:
            if os.path.exists(dir):
                print(f'{preCmdInfo}Directory checked: {cmdBlink(dir, "yellow")}')
            else:
                os.makedirs(dir)
                print(f'{preCmdInfo}Directory created: {cmdBlink(dir, "yellow")}')

def fileCheck(files: list) -> None:
    """
    Check if a file exists, if not create it
    """
    for file in files:
        if file:
            if os.path.exists(file): 
                print(f'{preCmdInfo}File checked: {cmdBlink(file, "yellow")}')
            else:
                with open(file, 'w') as f:
                    if file.endswith('.json'): 
                        print(f'{preCmdInfo}json file created: {cmdBlink(file, "yellow")}')
                        f.write('{}')
                    elif file.endswith('.csv'): 
                        print(f'{preCmdInfo}csv file created: {cmdBlink(file, "yellow")}')
                    else: f.write('')

def fileRenamer(old_name, new_name) -> bool:
    """
    Rename a file
    """
    current_time = getRunTime()
    new_name = f'{new_name}'.replace('.', f'{current_time}.')
    if os.path.exists(new_name): return False
    os.rename(old_name, new_name)
    return True
