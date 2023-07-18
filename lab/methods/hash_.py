from .color_ import(
    cmdBlink,
    ced
)

# -- HASH --

def getChanges(_loop, _key1, _key2) -> str:
    """
    returns a string with the changes between two keys
    """
    return ''.join(
        ced(_key2[i], color="yellow")
        if _key1[i] == _key2[i]
        else cmdBlink(_key2[i], 'green')
        for i in range(_loop)
    )

def extractObj(_job, _obj) -> str:
    """
    delete 'obj' from the end of 'job'
    """
    try:
        #> while _job ends with _obj..
        while _job[-1] == _obj:
            #> deletes _obj from the end of _job every time.
            _job = _job[:-1]
    except: pass
    return _job