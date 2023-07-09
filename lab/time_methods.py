from datetime import datetime

def getRunTime(): 
  return datetime.now().strftime('%d%m%Y%H%M%S')