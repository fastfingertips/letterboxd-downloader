import pandas as pd
import glob

# -- Local Imports -- #

from utils.log.custom import txtLog
from utils.color.custom import colored_text
from utils.file.custom import ensure_directories_exist

from constants.terminal import PRE_CMD_INFO
from constants.project import(
    PARTITION_LIMIT,
    PRE_LOG_INFO,
    SPLIT_LIMIT,
    SUP_LINE,
    SUB_LINE
)


# -- CSV Methods -- #

def splitCsv(_csvPath: str, _exportDirName: str, _currenSessionHash: int) -> None:
    """
    Splits a csv file into multiple csv files
    """
    splitCsvLines = open(_csvPath, 'r', encoding="utf8").readlines() # lines list
    csvMovies = len(splitCsvLines) # file line count
    if csvMovies > SPLIT_LIMIT: # file's line count is bigger than limit
        splitsPath = f'{_exportDirName}/Splits'
        splitCsvName = f'{splitsPath}/{_currenSessionHash}'
        ensure_directories_exist([splitsPath]) # split dir check
        defaultCsvCount = 1000 # optimal transfer count
        defaultPartition = 2 # starts from partition 2.
        splitFileNo = defaultPartition-1
        print(f'{PRE_CMD_INFO}Separation will be applied because there is movie({csvMovies}) over {SPLIT_LIMIT} in the file.')
        while True: # calculate how many partitions the file will be divided into.
            linesPerCsv = csvMovies/defaultPartition
            if (linesPerCsv <= defaultCsvCount and csvMovies % defaultPartition == 0):
                linesPerCsv = int(linesPerCsv) # we convert to int if remainder is zero.
                print(f'{PRE_CMD_INFO}{csvMovies} movie is splitting into {defaultPartition} parts.')
                break
            defaultPartition += 1

        if defaultPartition <= PARTITION_LIMIT: # default partition limit: 10
            for lineNo in range(csvMovies): # split file
                if lineNo % linesPerCsv == 0:
                    splitCsvLines.insert(lineNo+linesPerCsv,splitCsvLines[0]) #: keep header
                    open(f'{splitCsvName}-{splitFileNo}.csv', 'w+', encoding="utf8").writelines(splitCsvLines[lineNo:lineNo+linesPerCsv])
                    splitFileNo += 1
            print(f'{PRE_CMD_INFO}Ayrım işlemi {splitCsvName} adresinde sona erdi. Bölüm: [{defaultPartition}][{linesPerCsv}]')
        else:
            # if the separation limit is exceeded
            print(f'{PRE_CMD_INFO}Separation failed. Separation limit [{defaultPartition}/{PARTITION_LIMIT}] exceeded.')
    else:
        print(f'{PRE_CMD_INFO}There is a line/film({csvMovies}) under {SPLIT_LIMIT} in your file, the separation process will not be applied.')

def combineCsv(_urlList, _exportDirName, _currenSessionHash, _exportsPath) -> None:
    """
    Combines multiple csv files into one csv file
    """
    if len(_urlList) > 1:
        print(SUP_LINE)
        print(f"{PRE_CMD_INFO}{colored_text('Merge process info;', color='yellow')}")
        combineDir = f'{_exportDirName}/Combined/' # folder containing the combined lists
        combineCsvFile = f'{_currenSessionHash}_Normal-Combined.csv' # the name of the combine file.
        noDuplicateCsvFile = f'{_currenSessionHash}_NoDuplicate-Combined.csv' # NoDuplicate file name
        combineCsvPath = combineDir + combineCsvFile # path to the combine file.
        noDuplicateCsvPath = combineDir + noDuplicateCsvFile # NoDuplciate file path
        ensure_directories_exist([combineDir]) # combine dir check
        txtLog(f'{PRE_LOG_INFO}Lists will be combined because more than one list is being worked on.') # process logger

        try:
            try: allCsvFiles = list(glob.glob(f'{_exportsPath}*.csv')) # exporting all csv files in the specified directory to a variable.
            except: allCsvFiles = [i for i in glob.glob(f'{_exportsPath}*.csv')] # a different alternative
            combinedCsvFiles = pd.concat([pd.read_csv(f) for f in allCsvFiles]) # all csv files are merged.
            combinedCsvFiles.to_csv(combineCsvPath, index=False, encoding='utf-8-sig') # encode setting of the csv file.

            # https://stackoverflow.com/questions/15741564/removing-duplicate-rows-from-a-csv-file-using-a-python-script/15741627#15741627
            with open(combineCsvPath,'r', encoding="utf8") as in_file, open(noDuplicateCsvPath,'w', encoding="utf8") as out_file:
                #> to delete duplicate information..
                seen = set() # set for fast O(1) amortized lookup
                for line in in_file:
                    if line in seen: continue # skip duplicate
                    seen.add(line)
                    out_file.write(line)

            print(f'{PRE_CMD_INFO}All movies in lists have been saved to {combineCsvPath}.')
            print(f'{PRE_CMD_INFO}Only the file with different movies is set to {noDuplicateCsvPath} in the same directory.')
            splitCsv(noDuplicateCsvPath, _exportDirName, _currenSessionHash) # after extraction, we perform transfer splitting if necessary.
        except Exception as e: txtLog(f'Lists could not be combined. Error: {e}') #rocess logger
        print(SUB_LINE)
    else: txtLog('The process will not be combined because it is working on a single list.') # process logger


