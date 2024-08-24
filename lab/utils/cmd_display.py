from termcolor import colored as ced
from constants.project import SUP_LINE, SUB_LINE
from methods.color_ import preCmdInfo, preCmdMiddleDot, preCmdMiddleDotList

def coloredDictPrint(_coloredDict, _mainTitle=None) -> None:
    """
    Prints colored dict
    """
    print(SUP_LINE)
    if _mainTitle != None: 
        print(f"{preCmdInfo}{ced(f'{_mainTitle}', color='yellow')}")
    for listHeader in _coloredDict:
        print(f"{preCmdMiddleDot}{ced(listHeader, attrs=['bold', 'underline'])}")
        for listHeaderItem in _coloredDict[listHeader]:
            print(f"{preCmdMiddleDotList}{listHeaderItem}: {ced(_coloredDict[listHeader][listHeaderItem],'blue')}")
    print(SUB_LINE)