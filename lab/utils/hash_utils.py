from termcolor import colored as ced
from utils.cmd_format import cmd_blink

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
        ced(modified_text[i], color="yellow")
        if original_text[i] == modified_text[i]
        else cmd_blink(modified_text[i], 'green')
        for i in range(len(original_text))
    )

def extractObj(_job, _obj) -> str:
    """
    Deletes 'obj' from the end of 'job'
    """
    try:
        #> while _job ends with _obj..
        while _job[-1] == _obj:
            #> deletes _obj from the end of _job every time.
            _job = _job[:-1]
    except: 
        pass
    return _job
