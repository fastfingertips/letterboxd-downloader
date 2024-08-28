from termcolor import colored
from constants.terminal import ICON_MIDDLE_DOT_LIST, ICON_MIDDLE_DOT, ICON_INFO
from constants.project import SUP_LINE, SUB_LINE


def blink_text(msg: str, color: str) -> str:
    """
    Formats a message with a blinking effect and the specified color.

    Args:
        msg (str): The message to be formatted.
        color (str): The color to apply to the message.

    Returns:
        str: The formatted message with blinking effect and the specified color.
    """
    return colored(msg, color=color, attrs=["blink"])

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
        print(f"{ICON_INFO}{colored(title, color='yellow')}")
    
    for header, items in data.items():
        print(f"{ICON_MIDDLE_DOT}{colored(header, attrs=['bold', 'underline'])}")
        for item, value in items.items():
            print(f"{ICON_MIDDLE_DOT_LIST}{item}: {colored(value, color='blue')}")
    
    print(SUB_LINE)