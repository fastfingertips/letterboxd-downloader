from .color_ import ced, cmdBlink

def getChanges(loop,key1,key2):
    return ''.join(
        ced(key2[i], color="yellow")
        if key1[i] == key2[i]
        else cmdBlink(key2[i], 'green')
        for i in range(loop)
    )

def extractObj(job,obj):
    try:
        while job[-1] == obj: ## $job sonunda $obj olduğu sürece..
            job = job[:-1] # her defasında $job sonundan $obj siler.
    except: pass
    return job