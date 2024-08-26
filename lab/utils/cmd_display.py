from termcolor import colored as color_text

from constants.terminal import PRE_CMD_MIDDLE_DOT_LIST, PRE_CMD_MIDDLE_DOT, PRE_CMD_INFO
from constants.project import SUP_LINE, SUB_LINE

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
        print(f"{PRE_CMD_INFO}{color_text(title, color='yellow')}")
    
    for header, items in data.items():
        print(f"{PRE_CMD_MIDDLE_DOT}{color_text(header, attrs=['bold', 'underline'])}")
        for item, value in items.items():
            print(f"{PRE_CMD_MIDDLE_DOT_LIST}{item}: {color_text(value, color='blue')}")
    
    print(SUB_LINE)