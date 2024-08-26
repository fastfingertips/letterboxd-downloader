from termcolor import colored as ced
from utils.color.custom import format_command_message
from constants.project import CMD_PRINT_FILMS, SUP_LINE

# --- CONSTANTS ---

# Prefixes for different command messages
PRE_BLANK_COUNT = 4 * ' '  # Command message prefix blank calculation
PRE_CMD_INPUT = format_command_message('[>', 'green')  # Command input message prefix
PRE_CMD_INFO = format_command_message('[#', 'yellow')  # Command info message prefix
PRE_CMD_ERR = format_command_message('[!', 'red')  # Command error message prefix
PRE_CMD_CHECK = format_command_message('[✓', 'green')  # Command check message prefix
PRE_CMD_UNCHECK = format_command_message('[X', 'red')  # Command uncheck message prefix
PRE_CMD_MIDDLE_DOT = format_command_message(u'[\u00B7', 'cyan')  # Middle dot prefix for lists
PRE_CMD_MIDDLE_DOT_LIST = format_command_message(u' \u00B7', 'cyan')  # Middle dot list item prefix

# Conditional assignment for movies on the list
SUP_LINE_FILMS = (
    f'{SUP_LINE}\n{PRE_CMD_INFO}{ced("Movies on the list;", color="yellow")}\n'
    if CMD_PRINT_FILMS else ''
)