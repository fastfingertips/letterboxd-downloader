from termcolor import colored as ced
from utils.cmd_format import cmdBlink

def getChanges(_key1, _key2) -> str:
    """
    Returns a string with the changes between two keys
    """
    return ''.join(
        ced(_key2[i], color="yellow")
        if _key1[i] == _key2[i]
        else cmdBlink(_key2[i], 'green')
        for i in range(len(_key1))
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
