from constants.project import SUP_LINE, CMD_PRINT_FILMS, SUB_LINE
from termcolor import colored as ced #: [colored, cprint]


def cmdPre(m,c): #: Mesaj ön ekleri için kalıp.
    if m[0] == " ": return f' {ced(m[1:],color=c)}  '
    elif m[0] == "[": return f'[{ced(m[1:],color=c)}] '

# INITIAL ASSIGNMENTS
preBlankCount = 4*' ' # cmd msg pre blank calc
preCmdInput = cmdPre('[>','green') # cmd input msg pre
preCmdInfo = cmdPre('[#','yellow') # cmd info msg pre
preCmdErr = cmdPre('[!','red') # cmd error msg pre
preCmdCheck = cmdPre('[✓','green') # cmd check msg pre
preCmdUnCheck = cmdPre('[X','red') # cmd uncheck msg pre
preCmdMiddleDot, preCmdMiddleDotList  = cmdPre(u'[\u00B7','cyan'), cmdPre(u' \u00B7','cyan') #: Cmd middle dot pre
supLineFilms = f'{SUP_LINE}\n{preCmdInfo}{ced("Movies on the list;", color="yellow")}\n' if CMD_PRINT_FILMS else ''

def cmdBlink(m,c):
    return ced(m,c,attrs=["blink"])

def coloredDictPrint(colored_dict, main_title=None): # title, dict
    print(SUP_LINE)
    if main_title != None: print(f"{preCmdInfo}{ced(f'{main_title}', color='yellow')}")
    for listHeader in colored_dict:
        print(f"{preCmdMiddleDot}{ced(listHeader, attrs=['bold', 'underline'])}")
        for listHeaderItem in colored_dict[listHeader]:
            print(f"{preCmdMiddleDotList}{listHeaderItem}: {ced(colored_dict[listHeader][listHeaderItem],'blue')}")
    print(SUB_LINE)