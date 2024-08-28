from utils.color.custom import colored
from constants.project import CMD_PRINT_FILMS, SUP_LINE

def format_command_message(msg: str, color: str) -> str:
    """
    Formats a message with the specified color and adds surrounding formatting based on the message's content.

    Args:
        msg (str): The message to be formatted.
        color (str): The color to apply to the message.

    Returns:
        str: The formatted message with the specified color and additional formatting.

    Notes:
        - If the message starts with a space, it trims the space and applies color formatting.
        - If the message starts with a bracket '[', it applies color formatting inside the brackets.
        - If the message does not start with these patterns, no special formatting is applied.
    """
    if msg.startswith(" "):
        return f' {colored(msg[1:], color=color)}  '
    elif msg.startswith("["):
        return f'[{colored(msg[1:], color=color)}] '
    else:
        return colored(msg, color=color)

ICON_INFO = format_command_message('[#', 'yellow')
ICON_ERROR = format_command_message('[!', 'red')
ICON_CHECK = format_command_message('[✓', 'green')
ICON_INPUT = format_command_message('[>', 'green')
ICON_UNCHECK = format_command_message('[X', 'red')
ICON_QUESTION = format_command_message('[?', 'yellow')

ICON_MIDDLE_DOT = format_command_message(u'[\u00B7', 'cyan')
ICON_MIDDLE_DOT_LIST = format_command_message(u' \u00B7', 'cyan')

ICON_ARROW_RIGHT = colored('->', 'yellow')
ICON_ARROW_LEFT = colored('<-', 'yellow')

ICON_CIRCLE = colored('○', 'yellow')
ICON_CIRCLE_FULL = colored('●', 'yellow')

ICON_SQUARE = colored('□', 'yellow')
ICON_SQUARE_FULL = colored('■', 'yellow')

ICON_DIAMOND = colored('◇', 'yellow')
ICON_DIAMOND_FULL = colored('◆', 'yellow')

PRE_BLANK_COUNT = 4 * ' '  # Command message prefix blank calculation

SUP_LINE_FILMS = (
    f'{SUP_LINE}\n{ICON_INFO}{colored("Movies on the list;", color="yellow")}\n'
    if CMD_PRINT_FILMS else ''
)