from utils.color.custom import colored, format_command_message
from constants.project import CMD_PRINT_FILMS, SUP_LINE

ICON_INFO = format_command_message('[#', 'yellow')
ICON_ERROR = format_command_message('[!', 'red')
ICON_CHECK = format_command_message('[✓', 'green')
ICON_INPUT = format_command_message('[>', 'green')
ICON_UNCHECK = format_command_message('[X', 'red')
ICON_QUESTION = format_command_message('[?', 'yellow')

ICON_ARROW_RIGHT = colored('->', 'yellow')
ICON_ARROW_LEFT = colored('<-', 'yellow')

ICON_CIRCLE = colored('○', 'yellow')
ICON_CIRCLE_FULL = colored('●', 'yellow')

ICON_SQUARE = colored('□', 'yellow')
ICON_SQUARE_FULL = colored('■', 'yellow')

ICON_DIAMOND = colored('◇', 'yellow')
ICON_DIAMOND_FULL = colored('◆', 'yellow')

ICON_MIDDLE_DOT = format_command_message(u'[\u00B7', 'cyan')
ICON_MIDDLE_DOT_LIST = format_command_message(u' \u00B7', 'cyan')

PRE_BLANK_COUNT = 4 * ' '  # Command message prefix blank calculation

SUP_LINE_FILMS = (
    f'{SUP_LINE}\n{ICON_INFO}{colored("Movies on the list;", color="yellow")}\n'
    if CMD_PRINT_FILMS else ''
)