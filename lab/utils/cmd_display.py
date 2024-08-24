from termcolor import colored as ced
from constants.terminal import (
  PRE_CMD_MIDDLE_DOT_LIST,
  PRE_CMD_MIDDLE_DOT,
  PRE_CMD_INFO
)
from constants.project import (
  SUP_LINE,
  SUB_LINE
)
   

def coloredDictPrint(_coloredDict, _mainTitle=None) -> None:
    """
    Prints colored dict
    """
    print(SUP_LINE)
    if _mainTitle != None: 
        print(f"{PRE_CMD_INFO}{ced(f'{_mainTitle}', color='yellow')}")
    for listHeader in _coloredDict:
        print(f"{PRE_CMD_MIDDLE_DOT}{ced(listHeader, attrs=['bold', 'underline'])}")
        for listHeaderItem in _coloredDict[listHeader]:
            print(f"{PRE_CMD_MIDDLE_DOT_LIST}{listHeaderItem}: {ced(_coloredDict[listHeader][listHeaderItem],'blue')}")
    print(SUB_LINE)