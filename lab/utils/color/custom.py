from termcolor import colored as ced

def cmd_pre(msg: str, color: str) -> str:
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
        return f' {ced(msg[1:], color=color)}  '
    elif msg.startswith("["):
        return f'[{ced(msg[1:], color=color)}] '
    else:
        return ced(msg, color=color)

def cmd_blink(msg: str, color: str) -> str:
    """
    Formats a message with a blinking effect and the specified color.

    Args:
        msg (str): The message to be formatted.
        color (str): The color to apply to the message.

    Returns:
        str: The formatted message with blinking effect and the specified color.
    """
    return ced(msg, color=color, attrs=["blink"])
