from termcolor import colored as ced
from utils.cmd_format import cmdPre
from constants.project import CMD_PRINT_FILMS, SUP_LINE

# --- CONSTANTS ---

# Prefixes for different command messages
PRE_BLANK_COUNT = 4 * ' '  # Command message prefix blank calculation
PRE_CMD_INPUT = cmdPre('[>', 'green')  # Command input message prefix
PRE_CMD_INFO = cmdPre('[#', 'yellow')  # Command info message prefix
PRE_CMD_ERR = cmdPre('[!', 'red')  # Command error message prefix
PRE_CMD_CHECK = cmdPre('[✓', 'green')  # Command check message prefix
PRE_CMD_UNCHECK = cmdPre('[X', 'red')  # Command uncheck message prefix
PRE_CMD_MIDDLE_DOT = cmdPre(u'[\u00B7', 'cyan')  # Middle dot prefix for lists
PRE_CMD_MIDDLE_DOT_LIST = cmdPre(u' \u00B7', 'cyan')  # Middle dot list item prefix

# Conditional assignment for movies on the list
SUP_LINE_FILMS = (
    f'{SUP_LINE}\n{PRE_CMD_INFO}{ced("Movies on the list;", color="yellow")}\n'
    if CMD_PRINT_FILMS else ''
)