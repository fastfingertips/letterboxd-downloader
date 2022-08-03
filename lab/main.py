import csv, sys, os, json, glob, time #: PMI
from datetime import datetime #: PMI
from inspect import currentframe #: PMI
from numpy import partition #: PMI
while True: #: Other libs
    try:
        import arrow, requests, pandas as pd #: PMI
        from bs4 import BeautifulSoup as bs #: BeautifulSoup
        from termcolor import colored as ced #: [colored, cprint]
        # from libs.termcolor110.termcolor import colored
        break
    except ImportError as e: #: Trying import
        print('Import Error: ', e)
        os.system('pipreqs --encoding utf-8 --force') #: pipreqs kullanarak kurulmasını sağlıyoruz.
        os.system('pip install -r requirements.txt & pip list') #: pip list kullanarak kurulmuş modülleri listeliyoruz.
        
def dirCheck(dirs): # List
    for dir in dirs:
        if dir: 
            if os.path.exists(dir):
                txtLog(f'{preLogInfo}{dir} folder already exists.',logFilePath)
            else:   
                os.makedirs(dir)
                txtLog(f'{preLogInfo}{dir} folder created.',logFilePath) #: Oluşturulamaz ise bir izin hatası olabilir.
        print(f'{preCmdInfo}Directory checked: {cmdBlink(dir, "yellow")}')

def doPullFilms(tempLoopCount,tempCurrentDom): #: Filmleri çekiyoruz yazıyoruz
    try:
        # > Çekilen sayfa kodları, bir filtre uygulanarak daraltıldı.
        list_entries = tempCurrentDom.find('ul', attrs={'class': 'js-list-entries poster-list -p70 film-list clear film-details-list'})
        if list_entries is None: #: Eğer film listesi boş ise
            list_entries = tempCurrentDom.select_one('ul.film-list') 
            if list_entries is None:
                 list_entries = tempCurrentDom.select_one('ul.poster-list')
                 if list_entries is None:
                    list_entries = tempCurrentDom.select_one('ul.film-details-list')            
        film_details = list_entries.find_all("li")

        # > Filmleri ekrana ve dosyaya yazdırma işlemleri
        for currentFilm in film_details:
            # Oda ismini çektik
            movie = currentFilm.find('h2', attrs={'class': 'headline-2 prettify'})
            movieName = movie.find('a').text
            
            try: # Film yılı bazen boş olabiliyor. Önlem alıyoruz"
                movieYear = movie.find('small').text
            except:
                movieYear = "Yok"
            if cmdPrintFilms: # Kullanıcı eğer isterse çekilen filmler ekrana da yansıtılır.
                print(f"{tempLoopCount}: {movieName}, {movieYear}")
            writer.writerow([str(movieName), str(movieYear)]) # Her seferinde Csv dosyasına çektiğimiz bilgileri yazıyoruz.
            tempLoopCount += 1
        return tempLoopCount
    except Exception as e:
        errorLine(e)  
        txtLog('An error was encountered while obtaining movie information.', logFilePath)

def doReadPage(tempUrl): #: Url'si belirtilen sayfanın okunup, dom alınması.
    try:
        txtLog(f'{preLogInfo}Trying connect to [{tempUrl}]',logFilePath) #: Log dosyasına bağlantı başlangıcında bilgi veriliyor.        
        while True:
            #: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                urlResponseCode = requests.get(tempUrl,timeout=30)
                urlDom = bs(urlResponseCode.content.decode('utf-8'), 'html.parser')
                if urlDom != None:
                    return urlDom #: Return page dom
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.")
                print(str(e))            
                continue
            except requests.Timeout as e:
                print("OOPS!! Timeout Error")
                print(str(e))
                continue
            except requests.RequestException as e:
                print("OOPS!! General Error")
                print(str(e))
                continue
            except KeyboardInterrupt:
                print("Someone closed the program")
            except Exception as e:
                print('Hata:',e)
          #: Get page dom.
    except Exception as e: #: Dom edinirken hata gerçekleşirse..
        errorLine(e)  
        txtLog(f'{preLogErr}Connection to address failed [{tempUrl}]',logFilePath)

def doReset(): # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e:
        errorLine(e)
        txtLog(f'{preLogErr}Attempting to restart the program failed.', logFilePath)

def getListLastPageNo(): # Listenin son sayfasını öğren
    try:
        # Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al. Son'linin içindeki bağlantının metni bize kaç sayfalı bir listemiz olduğunuz verecek.
        txtLog(f'{preLogInfo}Listedeki sayfa sayısı denetleniyor..',logFilePath)
        lastPageNo = cListDom.find('div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        txtLog(f'{preLogInfo}Liste birden çok sayfaya ({lastPageNo}) sahiptir.',logFilePath)
        getMovieCount(lastPageNo)
    except AttributeError: ## Kontrolümüzde..
        txtLog(f'{preLogInfo}Birden fazla sayfa yok, bu liste tek sayfadır. {AttributeError}',logFilePath)                   
        lastPageNo = 1 #: Sayfa sayısı bilgisi alınamadığında sayfa sayısı 1 olarak işaretlenir.
        getMovieCount(lastPageNo) #: Sayfa bilgisi gönderiliyor.
    except Exception as e:
        errorLine(e)
    finally:
        txtLog(f'{preLogInfo}Sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPageNo} olduğu öğrenildi.',logFilePath)
        return lastPageNo

def getMovieCount(tempLastPageNo): # Film sayısını öğreniyoruz
    try:              
        try: # Son sayfaya bağlanıp, son sayfadaki film sayısını almak bir get isteği üretir ve programı yavaşlatır bu nedenle bir alternatif
            metaDescription = cListDom.find('meta', attrs={'name':'description'}).attrs['content']
            metaDescription = metaDescription[10:] #: açıklama kısmındaki 'A list of ' sonrası
            for i in range(6):
                try:
                    int(metaDescription[i]) 
                    ii = i+1
                except:
                    pass
            movieCount = metaDescription[:ii]
        except Exception as e: ## Listenin son sayfa işlemleri.
            lastPageDom = doReadPage(f'{currentUrListItemDetailPage}{tempLastPageNo}') #: Getting lastpage dom.
            lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li") #: Sayfa kodları çekildi.
            lastPageMoviesCount =  len(lastPageArticles) #: Film sayısı öğrenildi.
            movieCount = ((int(tempLastPageNo)-1)*100)+lastPageMoviesCount #: Toplam film sayısını belirlemek.
            txtLog(f"{preLogInfo}Listedeki film sayısı {movieCount} olarak bulunmuştur.",logFilePath) #: Film sayısı hesaplandıktan sonra ekrana yazdırılır.
        return movieCount #: Film sayısı çağrıya gönderilir.
    except Exception as e: ## Olası hata durumunda. (Dom edinirken)
        errorLine(e)
        txtLog('Error getting movie count.', logFilePath)
        txtLog(f'{preLogErr}An error occurred while obtaining the number of movies.',logFilePath)

def settingsFileSet(): #: Ayar dosyası kurulumu.
    if os.path.exists(settingsFileName):
        while True:
            try:
                with open(settingsFileName) as jsonFile:
                    jsonObject = json.load(jsonFile)
                    logDirName = jsonObject['log_dir']
                    exportDirName = jsonObject['export_dir']
                    break
            except Exception as e:
                errorLine(e)  
                txtLog(f'Ayarlarınız {e} nedeniyle alınamadı.',logFilePath)
    else:
        while True:
            try:
                print(f'{preCmdErr}The settings file could not be found. Please enter the required information.')
                logDirName = input(f'{preCmdInput}Log directory Name: ')
                exportDirName = input(f'{preCmdInput}Export directory Name: ')
                settings_dict = {
                    'log_dir': logDirName,
                    'export_dir': exportDirName,}
                with open(settingsFileName, 'w') as json_file:
                    json.dump(settings_dict, json_file)
                break
            except Exception as e:
                errorLine(e)   
                txtLog(f'Your settings could not be saved due to {e}.',logFilePath)
    return logDirName, exportDirName

def listSignature(): #: x: 0 start msg, 1 end msg
    try:
        try: ## Liste sayfasından bilgiler çekmeyi denemek.
            listBy = cListDom.select("[itemprop=name]")[0].text #: Liste sahibi ismi çekiliyor.
            listTitle = cListDom.select("[itemprop=title]")[0].text.strip() #: Liste başlığının ismini çekiliyor.
            listPublicationTime = cListDom.select(".published time")[0].text #: Liste oluşturulma tarihi çekiliyor.
            listPT = arrow.get(listPublicationTime).humanize() #: Liste oluşturulma tarihi düzenleniyor. Arrow: https://arrow.readthedocs.io/en/latest/      
            listLastPage = getListLastPageNo() #: Liste son sayfası öğreniliyor.
            listMovieCount =  getMovieCount(listLastPage) #: Listedeki film sayısı hesaplanıyor.  
            try: ## Filtre bilgilerini liste sayfasından edinmeyi denemek.
                domSelectedDecadeYear = cListDom.select(".smenu-subselected")[3].text + 'movies only was done by.' #: Liste sayfasından yıl aralık filtre bilgisi alınıyor.
                domSelectedGenre = cListDom.select(".smenu-subselected")[2].text + 'only movies.' #: Liste sayfasından tür filtre bilgisi alınıyor.
                domSelectedSortBy = cListDom.select(".smenu-subselected")[0].text + '.' #: Liste sayfasından sıralama filtre bilgisi alınıyor.
            except Exception as e: ## Filtre bilgileri edinirken bir hata oluşursa..
                txtLog(f'{preLogErr}Filtre bilgileri elde bir sorun gerçekleşti.',logFilePath)
                print('Filtre bilgileri elde bir sorun gerçekleşti.')
                domSelectedDecadeYear, domSelectedGenre, domSelectedSortBy = 3*'Unknown' #: Filtre bilgileri edinemediğinde her filtreye None eklenir.                                            

            try: ## Search list update time
                listUpdateTime = cListDom.select(".updated time")[0].text #: Liste düzenlenme vakti çekiliyor.
                listUT = arrow.get(listUpdateTime).humanize() #: Çekilen liste düzenlenme vakti okunmaya uygun hale getiriliyor.
            except Exception as e: #: Düzenleme vakti edinemezse..
                errorLine(e)
                listUT = 'No editing.' #: Hata alınırsa liste düzenlenmemiş varsayılır.
            finally: ## Kontrol sonu işlemleri.
                os.system(f'title {processState} Process: @{cListOwner}.')
                print(f"\n{preCmdInfo}Process State: {cmdBlink(processState,'green')}")
                print(supLine)
                print(f"{preCmdInfo}{ced('List info;', color='yellow')}")
                print(f"{preCmdMiddleDot}List by {ced(listBy,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Updated: {ced(listUT,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Published: {ced(listPT,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List title: {ced(listTitle, 'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Filters;")
                print(f"{preCmdMiddleDotList}Filtered as {ced(domSelectedDecadeYear,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDotList}Filtered as {ced(domSelectedGenre,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDotList}Movies sorted by {ced(domSelectedSortBy,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List hash: {ced(cListRunTime,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Sayfa sayısı: {ced(listLastPage,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Number of movies: {ced(listMovieCount,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List domain name: {ced(cListDomainName,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List URL: {ced(currentUrListItem,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Process URL: {ced(currentUrListItemDetail,'grey', attrs=['bold'])}")
            txtLog(f'{preLogInfo}İmza yazdırma sonu.',logFilePath)
        except Exception as e:
            errorLine(e)
            txtLog(f'{preLogErr}Liste bilgileri çekilirken hata.',logFilePath)
    except Exception as e: #: İmza seçimi başarısız.
        errorLine(e)
        txtLog(f'{preLogErr}İmza yüklenemedi. Program yine de devam etmeyi deneyecek.',logFilePath)

def userListCheck(_urlListItemDom): #: Kullanıcının girilen şekilde bir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        try: #: meta etiketinden veri almayı dener eğer yoksa liste değil.
            metaOgType = getMetaContent(_urlListItemDom,'og:type') 

            if metaOgType == "letterboxd:list": # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşılır.
                txtLog(f'{preLogInfo}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {metaOgType}',logFilePath)
                metaOgUrl = getMetaContent(_urlListItemDom,'og:url') #: Liste yönlendirmesi var mı bakıyoruz
                metaOgTitle = getMetaContent(_urlListItemDom, 'og:title')  #: Liste ismini alıyoruz. Örnek: 'Search results for best comedy'
                bodyDataOwner = getBodyContent(_urlListItemDom,'data-owner') #: Liste sahibinin kullanıcı ismi.
                print(f'{preCmdCheck}{ced("Found it: ", color="green")}@{ced(bodyDataOwner,"yellow")} "{ced(metaOgTitle,"yellow")}"') #: Liste sahibinin kullanıcı ismi ve liste ismi ekrana yazdırılır.
                if urlListItem == metaOgUrl or urlListItem+'/' == metaOgUrl: #: Girilen URL Meta ile aynıysa..
                    txtLog(f'{preLogInfo}Liste adresi yönlendirme içermiyor.',logFilePath)
                else: ## Girilen URL Meta ile uyuşmuyorsa..
                    print(f'{preCmdInfo}Girdiğiniz liste linki yönlendirme içeriyor.')
                    print(f'{preBlankCount}Muhtemelen liste ismi yakın bir zamanda değişildi veya hatalı girdiniz.')
                    print(f'{preBlankCount}({ced("+","red")}): {ced(urlListItem, color="yellow")} adresini')
                    if urlListItem in metaOgUrl:
                        msgInputUrl = ced(urlListItem, color="yellow")
                        msgMetaOgUrlChange = ced(metaOgUrl.replace(urlListItem,""), color="green")
                    else:
                        metaLoop = len(metaOgUrl)
                        msgInputUrl = ''
                        msgMetaOgUrlChange = getChanges(metaLoop,urlListItem,metaOgUrl)
                    print(f'{preBlankCount}({ced("+","green")}): {msgInputUrl}{msgMetaOgUrlChange} şeklinde değiştirdik.')
                txtLog(f'{preLogInfo}{urlListItem} listesi bulundu: {metaOgTitle}',logFilePath)
                currentListAvaliable = True
        except Exception as e:
            errorLine(e)
            metaOgUrl = ''
            currentListAvaliable = False
    except Exception as e:
        errorLine(e)
        currentListAvaliable = False
    finally:
        return currentListAvaliable, metaOgUrl

def test_pause(): #: Geliştirici duraklatmaları için kalıp.
    os.system(f"echo {preCmdInfo}{cmdBlink('Press enter to continue with the new session.','yellow')} & pause >nul")

def errorLine(e): #: Error Code generator
    cl = currentframe()
    txtLog(f'{preLogErr} Error on line {cl.f_back.f_lineno} Exception Message: {e}',logFilePath)

def txtLog(r_message, logFilePath): #: None: Kullanıcı log lokasyonunu belirtmese de olur.
    try: ## Denenecek işlemler..
        f = open(logFilePath, "a", encoding="utf-8")#: Eklemek üzere bir dosya açar, mevcut değilse dosyayı oluşturur
        f.writelines(f'{r_message}\n')
        f.close()
    except Exception as e:
            print(f'Loglama işlemi {e} nedeniyle başarısız.')

def getChanges(loop,key1,key2):
    change = ''
    for i in range(loop):
            # print(key1[i], key2[i], key1[i]==key2[i]) #: Dev test
            if key1[i] == key2[i]:
                change += ced(key2[i], color="yellow")
            else:
                change += cmdBlink(key2[i],'green')
    return change

def getMetaContent(dom,obj):
    return dom.find('meta', property=obj).attrs['content']

def getBodyContent(dom, obj):
    return dom.find('body').attrs[obj]

def getRunTime():
    return datetime.now().strftime('%d%m%Y%H%M%S')

def currentListDomainName(currentUrListItem):
    _f_ = '/list/'
    return currentUrListItem[currentUrListItem.index(_f_)+len(_f_):].replace('/',"")

def cmdPre(m,c): #: Mesaj ön ekleri için kalıp.
    if m[0] == " ":
        return f' {ced(m[1:],color=c)}  '
    elif m[0] == "[":
        return f'[{ced(m[1:],color=c)}] '

def cmdBlink(m,c):
    return ced(m,c,attrs=["blink"])

def combineCsv():
    if len(urlList) > 1:
        print(supLine)
        print(f"{preCmdInfo}{ced('Merge process info;', color='yellow')}")
        combineDir = exportDirName + '/Combined/' #: Kombine edilen listelerin barındığı klasör
        combineCsvFile = currenSessionHash + '_Normal-Combined.csv' #: Kombine dosyasının ismi.
        noDuplicateCsvFile = currenSessionHash + '_NoDuplicate-Combined.csv' #: NoDuplicate file name
        combineCsvPath = combineDir + combineCsvFile #: Kombine dosyasının yolu.
        noDuplicateCsvPath = combineDir + noDuplicateCsvFile #: NoDuplciate file path
        dirCheck([combineDir]) #: Combine dir check
        txtLog('Birden fazla liste üzerinde çalışıldığından listeler kombine edilecek.',logFilePath) #: Process logger
        try:
            allCsvFiles = [i for i in glob.glob(exportsPath+'*.{}'.format('csv'))] #: Belirtilmiş dizindeki tüm csv dosyalarının bir değişkene aktarılması.
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
            splitCsv(noDuplicateCsvPath) # Ayıklama sonrası, aktarma ayırması gerekliyse gerçekleştiriyoruz.
        except Exception as e:
            txtLog(f'Listeler kombine edilemedi. Hata: {e}',logFilePath) #: Process logger
        print(subLine)
    else: 
        txtLog('Tek liste üzerinde çalışıldığı için işlem kombine edilmeyecek.',logFilePath) #: Process logger

def splitCsv(splitCsvPath):
    splitCsvLines = open(splitCsvPath, 'r', encoding="utf8").readlines() #: lines list
    csvMovies = len(splitCsvLines) #: Dosyadaki satırların toplamı
    if  csvMovies > splitLimit: #: Dosyadaki satırların toplamı belirlenen limitten büyükse..
        splitsPath = f'{exportDirName}/Splits'
        splitCsvName = f'{splitsPath}/{currenSessionHash}'
        dirCheck([splitsPath]) # Yolu kontrol ediyoruz.
        defaultCsvCount = 1000 # En ideal aktarma sayısı
        defaultPartition = 2 # Bölüm 2'den başlar.
        splitFileNo = defaultPartition-1
        print(f'{preCmdInfo}Dosya içinde {splitLimit} üzeri film({csvMovies}) olduğu için ayrım uygulanacak.')
        while True: #: Dosyanın kaça bölüneceği hesaplanır.
            linesPerCsv = csvMovies/defaultPartition
            if linesPerCsv <= defaultCsvCount:
                if csvMovies % defaultPartition == 0: # float check
                    linesPerCsv = int(linesPerCsv) # kalan sıfırsa int'e çeviririz.
                    print(f'{preCmdInfo}{csvMovies} film, {defaultPartition} parçaya bölünüyor.')
                    break
            defaultPartition += 1

        if defaultPartition <= partitionLimit: #: Default partition limit: 10
            for lineNo in range(csvMovies): #: Dosyanın bölünmesi
                if lineNo % linesPerCsv == 0:
                    splitCsvLines.insert(lineNo+linesPerCsv,splitCsvLines[0]) #: keep header
                    open(f'{splitCsvName}-{splitFileNo}.csv', 'w+', encoding="utf8").writelines(splitCsvLines[lineNo:lineNo+linesPerCsv])
                    splitFileNo += 1
            print(f'{preCmdInfo}Ayrım işlemi {splitCsvName} adresinde sona erdi. Bölüm: [{defaultPartition}][{linesPerCsv}]')
        else: # Ayrım limiti aşılırsa
            print(f'{preCmdInfo}Ayrım işlemi gerçekleşmedi. Ayrım limiti [{defaultPartition}/{partitionLimit}] aşıldı.')
    else:
        print(f'{preCmdInfo}Dosyanız içerisinde {splitLimit} altında satır/film({csvMovies}) var, ayrım işlemi uygulanmayacak.')

def extractObj(job,obj):
    try:
        while job[-1] == obj: ## $job sonunda $obj olduğu sürece..
            job = job[:len(job)-1] #: Her defasında $job sonundan $obj siler.
    except:
        pass
    return job

def urlFix(x):
        urlListItemDom = doReadPage(x) #: Sayfa dom'u alınır.
        userListAvailable, approvedListUrl = userListCheck(urlListItemDom) #: Liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
        if userListAvailable: ## Liste kullanıma uygunsa..
            if approvedListUrl not in urlList: ## Doğrulanmış URL daha önce URL Listesine eklenmediyse..
                urlList.append(approvedListUrl) #: Doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
        return urlList

# INITIAL ASSIGNMENTS
if True:
    os.system(f'color & cls & title Welcome %USERNAME%.')
    # Domain
    siteProtocol, siteUrl = "https://", "letterboxd.com" #: Saf domain'in parçalanarak birleştirilmesi
    siteDomain = siteProtocol + siteUrl #: Saf domain'in parçalanarak birleştirilmesi
    # Cmd Pre
    preCmdMiddleDot,preCmdMiddleDotList  = cmdPre(u'[\u00B7','cyan'), cmdPre(u' \u00B7','cyan') #: Cmd middle dot pre
    preCmdInput = cmdPre('[>','green') #: Cmd input msg pre
    preCmdInfo = cmdPre('[#','yellow') #: Cmd info msg pre
    preCmdErr = cmdPre('[!','red') #: Cmd error msg pre
    preCmdCheck = cmdPre('[✓','green') #: Cmd error msg pre
    preCmdUnCheck = cmdPre('[X','red')
    preBlankCount = 4*' ' #: Cmd msg pre blank calc
    # Log Pre
    preLogInfo = "Info: " #: Log file ingo msg pre
    preLogErr = "Error: " #: Log file err msg pre  
    # Cmd Lines
    supLine = '_'*80 #: sup line lenght
    subLine = '¯'*80 #: sub line lenght
    ## Kullanıcı tarafından değiştirilebilir..
    settingsFileName = 'settings'+'.json'
    cmdPrintFilms = True #: Filmler ekrana yazılsın mı
    splitLimit = 1500
    partitionLimit = 10
    splitParameter = "split:"
    if cmdPrintFilms:
        supLineFilms = f'{supLine}\n{preCmdInfo}{ced("Movies on the list;", color="yellow")}\n'
    else:
        supLineFilms = ''

# STARTUP
sessionLoop = 0 #: While döngüne ait 
sessionStartHash =  getRunTime() #: Generate start hash
while True:
    logDirName, exportDirName = settingsFileSet() #: Set Export dir and Log dirs
    os.system('cls') #: İlk başlangıç ve yeni başlangıçlara temiz bir başlangıç.
    currenSessionHash = getRunTime() #: sessionHashes = {'Startup':sessionStartHash,'Current':currenSessionHash}
    hashChanges = getChanges(len(sessionStartHash),sessionStartHash,currenSessionHash)
    logFilePath = f'{logDirName}/{currenSessionHash}.txt' #: Set log file dir
    exportsPath = f'{exportDirName}/{currenSessionHash}/'
    print(f"{preCmdInfo}Session Hash: {sessionStartHash}{'' if sessionStartHash == currenSessionHash else ' -> ' + hashChanges}") #: Her oturum başlangıcı için farklı bir isim üretildi.
    dirCheck([logDirName,exportDirName]) #: Log file check     
    inputLoopNo, urlList, breakLoop, listEnterPassOn = 0, [], False, True #: While döngüne ait 
    while True:
        inputLoopNo += 1 #: Başlangıçta döngü değerini artırıyoruz.
        urlListItem = str(input(f'{preCmdInput}List URL[{inputLoopNo}]: ')).lower() #: Kullanıcıdan liste url'i alınması ve düzenlenmesi.
        if len(urlListItem) > 0: ## Giriş boş değilse..
            
            if urlListItem[0:len(splitParameter)] == splitParameter: # Split görevi.
                splitCsv(urlListItem[len(splitParameter):])
                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                continue
            
            if "." in urlListItem:
                if urlListItem[-1] == "." or urlListItem == ".":
                    if not urlListItem[0] == '?':
                        print(f'{preCmdInfo}Parametre tanındı, liste alım işlemi sonlandırıldı.')
                    breakLoop = True #: Url alımını sonlandıracak bilgi.

                    if urlListItem[0] == '?' or urlListItem == ".." or urlListItem[-2:] == "..": 
                        print(f'{preCmdInfo}Ek parametre tanındı, liste arama sonrası tüm listeler otomatik onaylanacak.')
                        listEnterPassOn, listEnter, autoEnterMsg = False , True, '[Auto]' # Otomatik onaylama yapacak bilgi.

                    if len(urlList) > 0: ## Url listesinde liste varsa..
                        break
                    else:
                        if not urlListItem[0] == '?':
                            try:
                                urlListItem = urlListItem.replace('?','')
                                urlListItem = extractObj(urlListItem,'.')
                                urlList = urlFix(urlListItem)
                                break
                            except:
                                print(f"{preCmdInfo}To finish, you must first specify a list.") #: Liste belirtmeden işlemi sonlandırmaya çalışan kullanıcılar bilgilendiriliyor.
                                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                                continue

                urlListItem = extractObj(urlListItem,'.')

            if urlListItem[0] == '?': 
                print(f'{preCmdInfo}Paremetre tanındı: Liste arama modu.')
                urlListItem = urlListItem[1:] #: Başlangıçdaki soru işaret kaldırıldı.
                if "!" in urlListItem: #: Son liste belirleyicisi
                    x = -1
                    for i in range(3): #: Sona en fazla 3 rakam girilebilir. letterboxd'da max bulubilen liste sayısı 250
                        if urlListItem[x-1] == "!":
                            endList = int(urlListItem[x:])
                            urlListItem = urlListItem[:x-1]
                        x += -1
                else:
                    endList = 'Not specified.' # Son liste için bir parametre belirtilmezse.
                searchList = f'https://letterboxd.com/search/lists/{urlListItem}/'
                searchListPreviewDom = doReadPage(searchList)

                try: #: Getting og:title
                    searchMetaTitle = getMetaContent(searchListPreviewDom,'og:title')
                except AttributeError:
                    print(searchListPreviewDom)
                    print(f"{preCmdErr}Meta etiketinden 'og:title' alınamadı.")
                    txtLog(f"Meta etiketinden 'og:title' alınamadı. Hata Mesajı: {AttributeError}", logFilePath)
                    searchMetaTitle = ''                    
                
                try: #: Getting og:url
                    searchLMetaUrl = getMetaContent(searchListPreviewDom,'og:url')
                except AttributeError:
                    print(f"{preCmdErr}Meta etiketinden 'og:url' alınamadı.")
                    txtLog(f"Meta etiketinden 'og:url' alınamadı. Hata Mesajı: {AttributeError}", logFilePath)
                    searchLMetaUrl = ''  

                try: #: Getting query msg
                    searchListsQCountMsg = searchListPreviewDom.find('h2', attrs={'class':'section-heading'}).text #: Kaç liste bulunduğu hakkında bilgi veren mesajı çekiyoruz.
                except AttributeError:
                    print(f"{preCmdErr}Bir etiketten 'arama karşılama mesajı' alınamadı.")
                    txtLog(f"Bir etiketten 'arama karşılama mesajı' alınamadı. Hata Mesajı: {AttributeError}", logFilePath)
                    searchListsQCountMsg = ''  
                
                try:
                    searchListsQLastsPage = searchListPreviewDom.find_all('li',attrs={'class':'paginate-page'})[-1].text #: Son sayfayı alıyoruz.
                except:
                    searchListsQLastsPage = 1 #: Alınamazsa sayfada tek sayfa olduğu varsayılır.
                finally:
                    print(supLine)
                    print(f"{preCmdInfo}{ced('Process info;', color='yellow')}")
                    print(f"{preCmdMiddleDot}{ced('Request;', color='yellow')}")
                    print(f"{preCmdMiddleDotList}Query: {ced(urlListItem,'grey',attrs=['bold'])}")
                    print(f"{preCmdMiddleDot}{ced('Request response;', color='yellow')}")
                    print(f"{preCmdMiddleDotList}Last list: {ced(endList,'grey',attrs=['bold'])}")
                    print(f'{preCmdMiddleDotList}{searchMetaTitle}')
                    print(f'{preCmdMiddleDotList}{searchListsQCountMsg}')
                    print(f"{preCmdMiddleDotList}Page URL: {ced(searchLMetaUrl,'grey',attrs=['bold'])}")   
                    print(f"{preCmdMiddleDotList}Last Page: {ced(searchListsQLastsPage,'grey',attrs=['bold'])}")
                    print(subLine)
                sayfa, liste = 0, 0
                for i in range(int(searchListsQLastsPage)):
                    sayfa += 1
                    connectionPage = searchList+f'page/{sayfa}'
                    searchListDom = doReadPage(connectionPage)
                    listsUrls = searchListDom.find_all('a', attrs={'class':'list-link'}) #: Okunmuş sayfadaki tüm listelerin adresleri.
                    print(supLine)
                    print(f"{preCmdInfo}{ced('Process info;', color='yellow')}") #: Process Title
                    print(f"{preCmdInfo}CP: {ced(sayfa,'grey',attrs=['bold'])}, PL: {ced(len(listsUrls),'grey',attrs=['bold'])}, CPURL: {ced(connectionPage,'grey',attrs=['bold'])}") #: CP: Current Page, PL: Page list, CPURL: Current Page Url
                    for listsUrl in listsUrls:
                        if liste == endList:
                            print(f"{preCmdInfo}Liste sayısı belirlenen sayıya ({ced(liste,'grey',attrs=['bold'])}) ulaştı.")
                            break
                        liste += 1
                        print(f'{preCmdInfo}P{sayfa}:L{liste}')
                        urlListItem = siteDomain+listsUrl.get('href') #: https://letterboxd.com + /user_name/list/list_name
                        userListAvailable, approvedListUrl = userListCheck(doReadPage(urlListItem))
                        if approvedListUrl not in urlList:
                            if userListAvailable:
                                urlList.append(approvedListUrl)
                                print(f"{preCmdCheck}{ced('Eklendi.','green')}")
                        else:
                            print(f'{preCmdUnCheck}Bu listeyi daha önce eklemişiz.')
                            liste -= 1
                    else:
                        continue
                    print(subLine)
                    break
                break

            if '/detail' in urlListItem: # detail remove
                urlListItem = urlListItem.replace('/detail','')

            urlListItemDom = doReadPage(urlListItem) #: Sayfa dom'u alınır.
            userListAvailable, approvedListUrl = userListCheck(urlListItemDom) #: Liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
            if userListAvailable: ## Liste kullanıma uygunsa..
                if approvedListUrl not in urlList: ## Doğrulanmış URL daha önce URL Listesine eklenmediyse..
                    urlList.append(approvedListUrl) #: Doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
                    if breakLoop: ## Kullanıcı URL sonunda nokta belirttiyse..
                        break #: URL alımını sonlandırıyoruz.
                else: ## Doğrulanmış URL daha önce işlem görecek URL listine eklenmiş ise..
                    print(f'{preCmdErr}You have already entered this address list.') #: URL'in daha önce girildiğini ekrana yazdırıyoruz.
                    inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
            else: ## Kullanıcının girdiği URL doğrulanmazsa..
                print(f"{preCmdInfo}You did not enter a valid url.")
                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
        else: ## Kullanıcı genişliğe sahip bir değer girmez ise..
            print(f"{preCmdInfo}Just enter a period to move on to the next steps. You can also add it at the end of the URL.")
            inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
    print(f"{preCmdInfo}List address acquisition terminated.") #: Liste url alımı sona erdğinde mesaj bastırılır.
    
    processLoopNo = 0 #: For döngüne ait 
    for currentUrListItem in urlList:
        processLoopNo += 1
        processState = f'[{processLoopNo}/{len(urlList)}]'
        currentUrListItemDetail = f'{currentUrListItem}detail/' # Url'e detail eklendi.
        currentUrListItemDetailPage = f'{currentUrListItemDetail}page/' #: Detaylı url'e sayfa gezintisi için parametre eklendi.
        cListDom = doReadPage(currentUrListItemDetail) #: Şu anki liste sayfasını oku.
        try:
            cListOwner = getBodyContent(cListDom,'data-owner') #: Liste sahibini al.
        except Exception as e:
            print(f'{preCmdErr}Liste sahibi bilgisi alınamadı')
            txtLog(f'Liste sahibi bilgisi alınamadı Hata: {e}',logFilePath)
            cListOwner = 'Unknown'
        cListDomainName = currentListDomainName(currentUrListItem) #: Liste domain ismini düzenleyerek alır.
        cListRunTime = getRunTime() #: Liste işlem vaktini al. 
        
        listSignature() #: Liste hakkında bilgiler bastırılır.
        if listEnterPassOn:
            listEnter = input(f"{preCmdInput}Press enter to confirm the entered information. ({cmdBlink('Enter', 'green')})")
            
            if listEnter == "":
                listEnter, autoEnterMsg = True, '[Manual]'
            elif listEnter == ".":
                listEnter, autoEnterMsg = True, '[Auto]'
                listEnterPassOn = False
                print(f'{preCmdInfo}Listeler otomatik olarak onaylanacak şekilde ayarlandı.')
            else:
                listEnter = False
                print(f"{preCmdInfo}The {ced('session was canceled','red', attrs=['dark'])} because you did not verify the information.")
                txtLog(f'{preLogInfo}The session was canceled because you did not verify the information.',logFilePath)
    
        if listEnter:
            txtLog(f'{preLogInfo}Şimdiki listeye erişim başlatılıyor.',logFilePath)
            print(f"{preCmdInfo}{ced(f'List confirmed. {autoEnterMsg}', color='green')}")
            
            lastPageNo = getListLastPageNo()
            openCsv = f'{exportsPath}{cListOwner}_{cListDomainName}_{cListRunTime}.csv' 
            dirCheck([exportsPath]) #: Export klasörünün kontrolü.
            with open(openCsv, 'w', newline='', encoding="utf-8") as csvFile: #: Konumda Export klasörü yoksa dosya oluşturmayacaktır.
                writer = csv.writer(csvFile)
                writer.writerow(["Title", "Year"]) #: Csv açıldıktan sonra en üste yazılacak başlıklar.
                
                loopCount = 1
                print(supLineFilms,end='')
                for x in range(int(lastPageNo)): #: Sayfa sayısı kadar döngü oluştur.
                    txtLog(f'Connecting to: {currentUrListItemDetailPage}{str(x+1)}',logFilePath) #: Sayfa numarasını log dosyasına yaz.
                    currentDom = doReadPage(f'{currentUrListItemDetailPage}{str(x+1)}') #: Sayfa dom'u alınır.
                    loopCount = doPullFilms(loopCount, currentDom) #: Filmleri al.
                csvFile.close() #: Açtığımız dosyayı manuel kapattık
            
            os.system(f'title {processState} completed!') #: Dosya oluşturulduğunda ekrana yazı yazılır.
            txtLog(f'{preLogInfo}{processState} completed!',logFilePath) #: Dosya oluşturulduğunda log dosyasına yazı yazılır.
            print(f'{preCmdInfo}{loopCount-1} film {cmdBlink(openCsv,"yellow")} dosyasına aktarıldı.') #: Filmerin hangi CSV dosyasına aktarıldığı ekrana yazdırılır.
            print(subLine) #: Alt satır ekrana yazdırılır.
            print(f"{preCmdInfo}{ced(f'{processState} completed!', color='green')}") #: İşlem tamamlandığında mesajı ekrana yazdırıyoruz.
            
    combineCsv() #: Csv dosyalarını birleştir.
    os.system(f'title Session: {currenSessionHash} ended!') #: Session sonlandırıldığında ekrana yazdırılır.
    print(f"{preCmdInfo}Process State: {cmdBlink(processState +' Finish.','green')}") # Process durumunu ekrana yazdırıyoruz.
    print(f'{preCmdInfo}{ced(f"Session: {currenSessionHash} ended.", color="green")}') # Session sonlandırıldığında mesaj bastırılır.
    txtLog(f'{preLogInfo}Session: {currenSessionHash} ended.',logFilePath) # Session sonlandırıldığında log dosyasına yazılır.
    test_pause() #: Test için beklemeye yarar.
    
