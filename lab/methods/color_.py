from constants.project import(
    CMD_PRINT_FILMS,
    SUP_LINE,
    SUB_LINE
)

from termcolor import colored as ced

def cmdPre(_msg, _color):
    if _msg[0] == " ": return f' {ced(_msg[1:],color=_color)}  '
    elif _msg[0] == "[": return f'[{ced(_msg[1:],color=_color)}] '

# INITIAL ASSIGNMENTS
preBlankCount = 4*' ' # cmd msg pre blank calc
preCmdInput = cmdPre('[>','green') # cmd input msg pre
preCmdInfo = cmdPre('[#','yellow') # cmd info msg pre
preCmdErr = cmdPre('[!','red') # cmd error msg pre
preCmdCheck = cmdPre('[✓','green') # cmd check msg pre
preCmdUnCheck = cmdPre('[X','red') # cmd uncheck msg pre
preCmdMiddleDot, preCmdMiddleDotList  = cmdPre(u'[\u00B7','cyan'), cmdPre(u' \u00B7','cyan') #: cmd middle dot pre
supLineFilms = f'{SUP_LINE}\n{preCmdInfo}{ced("Movies on the list;", color="yellow")}\n' if CMD_PRINT_FILMS else ''

def cmdBlink(_msg, _color):
    return ced(_msg, _color, attrs=["blink"])

def coloredDictPrint(_coloredDict, _mainTitle=None): # title, dict
    print(SUP_LINE)
    if _mainTitle != None: print(f"{preCmdInfo}{ced(f'{_mainTitle}', color='yellow')}")
    for listHeader in _coloredDict:
        print(f"{preCmdMiddleDot}{ced(listHeader, attrs=['bold', 'underline'])}")
        for listHeaderItem in _coloredDict[listHeader]:
            print(f"{preCmdMiddleDotList}{listHeaderItem}: {ced(_coloredDict[listHeader][listHeaderItem],'blue')}")
    print(SUB_LINE)