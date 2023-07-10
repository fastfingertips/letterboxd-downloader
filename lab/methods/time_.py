from datetime import datetime #: PMI

def getRunTime():
    return datetime.now().strftime('%d%m%Y%H%M%S')

def getLogTime():
    return datetime.now().strftime('%d/%m/%Y %H:%M:%S')