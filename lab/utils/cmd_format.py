from termcolor import colored as ced

def cmdPre(_msg, _color) -> str:
    """
    Returns the message with the color and pre
    """
    if _msg[0] == " ": 
        return f' {ced(_msg[1:], color=_color)}  '
    elif _msg[0] == "[":
        return f'[{ced(_msg[1:], color=_color)}] '

def cmdBlink(_msg, _color) -> str:
    """
    Blinking cmd msg
    """
    return ced(_msg, _color, attrs=["blink"])