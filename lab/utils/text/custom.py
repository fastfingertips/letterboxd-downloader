import logging
from utils.color.custom import colored, blink_text

def highlight_changes(original_text: str, modified_text: str) -> str:
    """
    Highlights the changes between two strings by comparing them character by character.

    Characters that remain the same between the two strings are highlighted in yellow.
    Characters that differ are highlighted in green with a blinking effect.

    Args:
        original_text (str): The original string to compare.
        modified_text (str): The modified string to compare.

    Returns:
        str: A string with highlighted differences.
    """
    return ''.join(
        colored(modified_text[i], color="yellow")
        if original_text[i] == modified_text[i]
        else blink_text(modified_text[i], 'green')
        for i in range(len(original_text))
    )

def trim_end(text: str, char_to_remove: str) -> str:
    """
    Removes all instances of a specified character from the end of a string.

    Args:
        text (str): The string from which to remove the trailing characters.
        char_to_remove (str): The character to remove from the end of the string.

    Returns:
        str: The string with the specified trailing character removed.
    """
    try:
        # Continue removing the character while it is present at the end of the string.
        while text.endswith(char_to_remove):
            text = text[:-1]
    except Exception as e: 
        # Log the error if necessary or handle it appropriately.
        logging.error(f"Error while trimming characters: {e}")
    return text

def remove_substring(main_string: str, substring: str) -> str:
    """
    Removes the specified substring from the main string if it exists.

    Args:
        main_string (str): The string from which to remove the substring.
        substring (str): The substring to remove from the main string.

    Returns:
        str: The modified string with the substring removed if it was found, otherwise the original string.
    """
    if substring in main_string:
        return main_string.replace(substring, "")
    return main_string