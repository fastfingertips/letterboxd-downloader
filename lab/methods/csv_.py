from constants.project import SPLIT_LIMIT, PARTITION_LIMIT, SUP_LINE, PRE_LOG_INFO, SUB_LINE
from .system_ import dirCheck
from .log_ import txtLog
from .color_ import preCmdInfo, ced
import glob
import pandas as pd #: PMI

def splitCsv(split_csv_path, exportDirName, currenSessionHash):
    splitCsvLines = open(split_csv_path, 'r', encoding="utf8").readlines() # lines list
    csvMovies = len(splitCsvLines) # dosyadaki satırların toplamı
    if csvMovies > SPLIT_LIMIT: # dosyadaki satırların toplamı belirlenen limitten büyükse..
        splitsPath = f'{exportDirName}/Splits'
        splitCsvName = f'{splitsPath}/{currenSessionHash}'
        dirCheck([splitsPath]) # yolu kontrol ediyoruz.
        defaultCsvCount = 1000 # en ideal aktarma sayısı
        defaultPartition = 2 # bölüm 2'den başlar.
        splitFileNo = defaultPartition-1
        print(f'{preCmdInfo}Dosya içinde {SPLIT_LIMIT} üzeri film({csvMovies}) olduğu için ayrım uygulanacak.')
        while True: # dosyanın kaça bölüneceği hesaplanır.
            linesPerCsv = csvMovies/defaultPartition
            if (linesPerCsv <= defaultCsvCount and csvMovies % defaultPartition == 0):
                linesPerCsv = int(linesPerCsv) # kalan sıfırsa int'e çeviririz.
                print(f'{preCmdInfo}{csvMovies} film, {defaultPartition} parçaya bölünüyor.')
                break
            defaultPartition += 1

        if defaultPartition <= PARTITION_LIMIT: # default partition limit: 10
            for lineNo in range(csvMovies): # dosyanın bölünmesi
                if lineNo % linesPerCsv == 0:
                    splitCsvLines.insert(lineNo+linesPerCsv,splitCsvLines[0]) #: keep header
                    open(f'{splitCsvName}-{splitFileNo}.csv', 'w+', encoding="utf8").writelines(splitCsvLines[lineNo:lineNo+linesPerCsv])
                    splitFileNo += 1
            print(f'{preCmdInfo}Ayrım işlemi {splitCsvName} adresinde sona erdi. Bölüm: [{defaultPartition}][{linesPerCsv}]')
        else: print(f'{preCmdInfo}Ayrım işlemi gerçekleşmedi. Ayrım limiti [{defaultPartition}/{PARTITION_LIMIT}] aşıldı.') # ayrım limiti aşılırsa
    else: print(f'{preCmdInfo}Dosyanız içerisinde {SPLIT_LIMIT} altında satır/film({csvMovies}) var, ayrım işlemi uygulanmayacak.')

def combineCsv(urlList, exportDirName, currenSessionHash, exportsPath):
    if len(urlList) > 1:
        print(SUP_LINE)
        print(f"{preCmdInfo}{ced('Merge process info;', color='yellow')}")
        combineDir = f'{exportDirName}/Combined/' #: Kombine edilen listelerin barındığı klasör
        combineCsvFile = f'{currenSessionHash}_Normal-Combined.csv' #: Kombine dosyasının ismi.
        noDuplicateCsvFile = f'{currenSessionHash}_NoDuplicate-Combined.csv' #: NoDuplicate file name
        combineCsvPath = combineDir + combineCsvFile #: Kombine dosyasının yolu.
        noDuplicateCsvPath = combineDir + noDuplicateCsvFile #: NoDuplciate file path
        dirCheck([combineDir]) #: Combine dir check
        txtLog(f'{PRE_LOG_INFO}Birden fazla liste üzerinde çalışıldığından listeler kombine edilecek.') #: Process logger

        try:
            try: allCsvFiles = list(glob.glob(f'{exportsPath}*.csv')) #: Belirtilmiş dizindeki tüm csv dosyalarının bir değişkene aktarılması.
            except: allCsvFiles = [i for i in glob.glob(f'{exportsPath}*.csv')] #: Farklı bir alternatif
            combinedCsvFiles = pd.concat([pd.read_csv(f) for f in allCsvFiles]) #: Csv dosyalarının tümü birleştirilir.
            combinedCsvFiles.to_csv(combineCsvPath, index=False, encoding='utf-8-sig') #: Csv dosyasının encod ayarı.
            ## https://stackoverflow.com/questions/15741564/removing-duplicate-rows-from-a-csv-file-using-a-python-script/15741627#15741627

            with open(combineCsvPath,'r', encoding="utf8") as in_file, open(noDuplicateCsvPath,'w', encoding="utf8") as out_file: ## Tekrarlayan bilgileri silmek için..
                seen = set() # set for fast O(1) amortized lookup
                for line in in_file:
                    if line in seen: continue # skip duplicate
                    seen.add(line)
                    out_file.write(line)

            print(f'{preCmdInfo}Listelerdeki tüm filmler {combineCsvPath} dosyasına kaydedildi.')
            print(f'{preCmdInfo}Yalnızca farklı fimlerin olduğu dosya aynı dizinde {noDuplicateCsvPath} olarak ayarlandı.')
            splitCsv(noDuplicateCsvPath, exportDirName, currenSessionHash) # Ayıklama sonrası, aktarma ayırması gerekliyse gerçekleştiriyoruz.
        except Exception as e: txtLog(f'Listeler kombine edilemedi. Hata: {e}') #: Process logger
        print(SUB_LINE)
    else: txtLog('Tek liste üzerinde çalışıldığı için işlem kombine edilmeyecek.') #: Process logger


