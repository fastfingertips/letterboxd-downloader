from termcolor import colored

from constants.terminal import PRE_CMD_MIDDLE_DOT_LIST, PRE_CMD_MIDDLE_DOT, PRE_CMD_INFO
from constants.project import SUP_LINE, SUB_LINE

def colored_text(text: str, color: str) -> None:
    """
    Prints the given text in the specified color.

    Args:
        text (str): The text to be printed.
        color (str): The color to be used for the text.
    """
    return colored(text, color)

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
        return f' {colored_text(msg[1:], color=color)}  '
    elif msg.startswith("["):
        return f'[{colored_text(msg[1:], color=color)}] '
    else:
        return colored_text(msg, color=color)

def blink_text(msg: str, color: str) -> str:
    """
    Formats a message with a blinking effect and the specified color.

    Args:
        msg (str): The message to be formatted.
        color (str): The color to apply to the message.

    Returns:
        str: The formatted message with blinking effect and the specified color.
    """
    return colored_text(msg, color=color, attrs=["blink"])

def print_colored_dict(data: dict, title: str = None) -> None:
    """
    Prints a dictionary with colored text formatting.

    The function prints a dictionary where each key and value pair is formatted with specific colors.
    The main title, if provided, is printed in yellow.

    Args:
        data (dict): The dictionary to print. Keys are headers and values are dictionaries of items.
        title (str, optional): The title to be printed above the dictionary. Defaults to None.
    """
    print(SUP_LINE)
    
    if title:
        print(f"{PRE_CMD_INFO}{colored_text(title, color='yellow')}")
    
    for header, items in data.items():
        print(f"{PRE_CMD_MIDDLE_DOT}{colored_text(header, attrs=['bold', 'underline'])}")
        for item, value in items.items():
            print(f"{PRE_CMD_MIDDLE_DOT_LIST}{item}: {colored_text(value, color='blue')}")
    
    print(SUB_LINE)