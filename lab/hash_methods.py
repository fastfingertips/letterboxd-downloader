from color_methods import ced, cmdBlink

def getChanges(loop,key1,key2):
    return ''.join(
        ced(key2[i], color="yellow")
        if key1[i] == key2[i]
        else cmdBlink(key2[i], 'green')
        for i in range(loop)
    )