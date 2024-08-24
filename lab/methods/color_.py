from termcolor import colored as ced
from utils.cmd_format import cmdPre
from constants.project import(
    CMD_PRINT_FILMS,
    SUP_LINE
)

# INITIAL ASSIGNMENTS
preBlankCount = 4*' ' # cmd msg pre blank calc
preCmdInput = cmdPre('[>','green') # cmd input msg pre
preCmdInfo = cmdPre('[#','yellow') # cmd info msg pre
preCmdErr = cmdPre('[!','red') # cmd error msg pre
preCmdCheck = cmdPre('[✓','green') # cmd check msg pre
preCmdUnCheck = cmdPre('[X','red') # cmd uncheck msg pre
preCmdMiddleDot, preCmdMiddleDotList  = cmdPre(u'[\u00B7','cyan'), cmdPre(u' \u00B7','cyan') #: cmd middle dot pre
supLineFilms = f'{SUP_LINE}\n{preCmdInfo}{ced("Movies on the list;", color="yellow")}\n' if CMD_PRINT_FILMS else ''