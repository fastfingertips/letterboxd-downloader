from termcolor import colored as ced #: [colored, cprint]
from constants import *



def cmdPre(m,c): #: Mesaj ön ekleri için kalıp.
    if m[0] == " ": return f' {ced(m[1:],color=c)}  '
    elif m[0] == "[": return f'[{ced(m[1:],color=c)}] '

def cmdBlink(m,c): 
   return ced(m,c,attrs=["blink"])


# INITIAL ASSIGNMENTS
preBlankCount = 4*' ' # cmd msg pre blank calc
preCmdInput = cmdPre('[>','green') # cmd input msg pre
preCmdInfo = cmdPre('[#','yellow') # cmd info msg pre
preCmdErr = cmdPre('[!','red') # cmd error msg pre
preCmdCheck = cmdPre('[✓','green') # cmd check msg pre
preCmdUnCheck = cmdPre('[X','red') # cmd uncheck msg pre
preCmdMiddleDot, preCmdMiddleDotList  = cmdPre(u'[\u00B7','cyan'), cmdPre(u' \u00B7','cyan') #: Cmd middle dot pre
supLineFilms = f'{SUP_LINE}\n{preCmdInfo}{ced("Movies on the list;", color="yellow")}\n' if CMD_PRINT_FILMS else ''