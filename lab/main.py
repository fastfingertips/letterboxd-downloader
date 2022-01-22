import csv, sys, os, json, glob, time #: PMI
from datetime import datetime #: PMI
from inspect import currentframe
from tkinter import N

from attr import attr #: PMI
while True: #: Other libs
    try:
        import arrow
        import requests
        from bs4 import BeautifulSoup
        from termcolor import colored, cprint
        import pandas as pd
        # from libs.termcolor110.termcolor import colored
        break
    except ImportError as e: #: Trying import
        print('Impor Error: ', e)
        os.system('pipreqs --encoding utf-8 --force')
        os.system('pip install -r requirements.txt & pip list')
        
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
        articles = tempCurrentDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
        # > Filmleri ekrana ve dosyaya yazdırma işlemleri
        for currentArticle in articles:
            # Oda ismini çektik
            movie = currentArticle.find('h2', attrs={'class': 'headline-2 prettify'})
            movieName = movie.find('a').text
            # Film yılı bazen boş olabiliyor. Önlem alıyoruz"
            try:
                movieYear = movie.find('small').text
            except:
                movieYear = "Yok"
            # Her seferinde Csv dosyasına çektiğimiz bilgileri yazıyoruz.
            if cmdPrintFilms:
                print(f" {tempLoopCount}: {movieName}, {movieYear}")
            writer.writerow([str(movieName), str(movieYear)])
            tempLoopCount += 1
        return tempLoopCount
    except Exception as e:
        errorLine(e)  
        txtLog('An error was encountered while obtaining movie information.', logFilePath)

def doReadPage(tempUrl): #: Url'si belirtilen sayfanın okunup, dom alınması.
    try:
        txtLog(f'{preLogInfo}Trying connect to [{tempUrl}]',logFilePath)                            #: Log dosyasına bağlantı başlangıcında bilgi veriliyor.        
        while True:
            #: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                urlResponseCode = requests.get(tempUrl,timeout=30)
                urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')
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
    except Exception as e:
        errorLine(e)                                                                #: Dom edinirken hata gerçekleşirse..
        txtLog(f'{preLogErr}Connection to address failed [{tempUrl}]',logFilePath)

def doReset():  # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e:
        errorLine(e)
        txtLog(preLogErr + 'Attempting to restart the program failed.',logFilePath)

def getListLastPageNo():  # Listenin son sayfasını öğren
    try:
        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
        txtLog(f'{preLogInfo}Listedeki sayfa sayısı denetleniyor..',logFilePath)
        lastPageNo = cListDom.find('div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text    # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        txtLog(f'{preLogInfo}Liste birden çok sayfaya ({lastPageNo}) sahiptir.',logFilePath)
        getMovieCount(lastPageNo)
    except AttributeError:                                                                            ## Kontrolümüzde..
        txtLog(f'{preLogInfo}Birden fazla sayfa yok, bu liste tek sayfadır. {AttributeError}',logFilePath)                   
        lastPageNo = 1                                                                          #: Sayfa sayısı bilgisi alınamadığında sayfa sayısı 1 olarak işaretlenir.
        getMovieCount(lastPageNo)                                                               #: Sayfa bilgisi gönderiliyor.
    except Exception as e:
        errorLine(e)
    finally:
        txtLog(f'{preLogInfo}Sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPageNo} olduğu öğrenildi.',logFilePath)
        return lastPageNo

def getMovieCount(tempLastPageNo):  # Film sayısını öğreniyoruz
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
            lastPageDom = doReadPage(f'{currentUrListItemDetailPage}{tempLastPageNo}')                                                                              #: Getting lastpage dom.
            lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li") #: Sayfa kodları çekildi.
            lastPageMoviesCount =  len(lastPageArticles)                                                                                    #: Film sayısı öğrenildi.
            movieCount = ((int(tempLastPageNo)-1)*100)+lastPageMoviesCount                                                                  #: Toplam film sayısını belirlemek.
            txtLog(f"{preLogInfo}Listedeki film sayısı {movieCount} olarak bulunmuştur.",logFilePath)                                                   #: Film sayısı hesaplandıktan sonra ekrana yazdırılır.
        return movieCount                                                                                                               #: Film sayısı çağrıya gönderilir.
    except Exception as e:
        errorLine(e)          
        txtLog(f'Error getting movie count.',logFilePath)                                                      #: Dom edinirken hata gerçekleşirse..                                                                                                                        ## Olası hata durumunda.
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
                    'export_dir': exportDirName,
                }
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
                print(f"{preCmdInfo}{colored('List info;', color='yellow')}")
                print(f"{preCmdMiddleDot}List by {colored(listBy,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Updated: {colored(listUT,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Published: {colored(listPT,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List title: {colored(listTitle, 'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Filters;")
                print(f"{preCmdMiddleDotList}Filtered as {colored(domSelectedDecadeYear,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDotList}Filtered as {colored(domSelectedGenre,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDotList}Movies sorted by {colored(domSelectedSortBy,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List hash: {colored(cListRunTime,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Sayfa sayısı: {colored(listLastPage,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Number of movies: {colored(listMovieCount,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List domain name: {colored(cListDomainName,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List URL: {colored(currentUrListItem,'grey', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Process URL: {colored(currentUrListItemDetail,'grey', attrs=['bold'])}")
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
                print(f'{preCmdCheck}{colored("Found it: ", color="green")}@{colored(bodyDataOwner,"yellow")} "{colored(metaOgTitle,"yellow")}"') #: Liste sahibinin kullanıcı ismi ve liste ismi ekrana yazdırılır.
                if urlListItem == metaOgUrl or urlListItem+'/' == metaOgUrl: #: Girilen URL Meta ile aynıysa..
                    txtLog(f'{preLogInfo}Liste adresi yönlendirme içermiyor.',logFilePath)
                else: ## Girilen URL Meta ile uyuşmuyorsa..
                    print(f'{preCmdInfo}Girdiğiniz liste linki yönlendirme içeriyor.')
                    print(f'{preBlankCount}Muhtemelen liste ismi yakın bir zamanda değişildi veya hatalı girdiniz.')
                    print(f'{preBlankCount}({colored("+","red")}): {colored(urlListItem, color="yellow")} adresini')
                    if urlListItem in metaOgUrl:
                        msgInputUrl = colored(urlListItem, color="yellow")
                        msgMetaOgUrlChange = colored(metaOgUrl.replace(urlListItem,""), color="green")
                    else:
                        metaLoop = len(metaOgUrl)
                        msgInputUrl = ''
                        msgMetaOgUrlChange = getChanges(metaLoop,urlListItem,metaOgUrl)
                    print(f'{preBlankCount}({colored("+","green")}): {msgInputUrl}{msgMetaOgUrlChange} şeklinde değiştirdik.')
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
                change += colored(key2[i], color="yellow")
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
        return f' {colored(m[1:],color=c)}  '
    elif m[0] == "[":
        return f'[{colored(m[1:],color=c)}] '

def cmdBlink(m,c):
    return colored(m,c,attrs=["blink"])

def combineCsv():
    if len(urlList) > 1:
        print(supLine)
        print(f"{preCmdInfo}{colored('Merge process info;', color='yellow')}")
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
            print(f'{preCmdInfo}Yalnızca farklı fimlerin olduğu dosya {noDuplicateCsvPath} olarak ayarlandı.')
        except Exception as e:
            txtLog(f'Listeler kombine edilemedi. Hata: {e}',logFilePath) #: Process logger
        print(subLine)
    else: 
        txtLog('Tek liste üzerinde çalışıldığı için işlem kombine edilmeyecek.',logFilePath) #: Process logger

def splitCsv(csvPath):
    dirCheck(['splits'])
    csvfile = open(csvPath, 'r', encoding="utf8").readlines() #: lines list
    if len(csvfile) > 5000: 
        filename = 1
        split = 1500
        for i in range(len(csvfile)):
            if i % split == 0:
                csvfile.insert(i+split,csvfile[0]) #: keep header
                open(f'splits/{filename}.csv', 'w+', encoding="utf8").writelines(csvfile[i:i+split])
                filename += 1

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

    if cmdPrintFilms:
        supLineFilms = f'{supLine}\n{preCmdInfo}{colored("Movies on the list;", color="yellow")}\n'
    else:
        supLineFilms = ''

# STARTUP
sessionLoop = 0 #: While döngüne ait 
sessionStartHash =  getRunTime() #: Generate start hash
while True:
    logDirName, exportDirName = settingsFileSet() #: Set Export dir and Log dir
    os.system('cls') #: İlk başlangıç ve yeni başlangıçlara temiz bir başlangıç.
    currenSessionHash = getRunTime() #: sessionHashes = {'Startup':sessionStartHash,'Current':currenSessionHash}
    hashChanges = getChanges(len(sessionStartHash),sessionStartHash,currenSessionHash)
    logFilePath = f'{logDirName}/{currenSessionHash}.txt' #: Set log file dir
    exportsPath = f'{exportDirName}/{currenSessionHash}/'
    print(f"{preCmdInfo}Session Hash: {sessionStartHash}{'' if sessionStartHash == currenSessionHash else ' -> ' + hashChanges}") #: Her oturum başlangıcı için farklı bir isim üretildi.
    dirCheck([logDirName,exportDirName]) #: Log file check     
    inputLoopNo, urlList, breakLoop = 0, [], False #: While döngüne ait 
    while True:
        inputLoopNo += 1 #: Başlangıçta döngü değerini artırıyoruz.
        urlListItem = str(input(f'{preCmdInput}List URL[{inputLoopNo}]: ')).lower() #: Kullanıcıdan liste url'i alınması ve düzenlenmesi.
        if len(urlListItem) > 0: ## Giriş boş değilse..
            if urlListItem == ".": ## Sadece nokta girildiyse..
                if len(urlList) > 0: ## Url listesinde liste varsa..
                    break
                else: ## Url listesinde liste yoksa..
                    print(f"{preCmdInfo}To finish, you must first specify a list.") #: Liste belirtmeden işlemi sonlandırmaya çalışan kullanıcılar bilgilendiriliyor.
                    inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                    continue
            elif urlListItem[-1] == ".": ## Girilen url sonunda nokta varsa..
                breakLoop = True #: Url alımını sonlandıracak bilgi.
                while urlListItem[-1] == ".": ## Url sonunda nokta olduğu sürece..
                    urlListItem = urlListItem[:len(urlListItem)-1] #: Her defasında Url sonundan nokta siler.
            elif urlListItem[0:6] == 'split:':
                splitCsv(urlListItem[6:])
                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                continue
            elif urlListItem[0] == '?': ## Giriş başlangıcında soru işareti varsa.. (Liste arama moduna geçilir.)
                print(f'{preCmdInfo}Parameter recognized, searching list.')
                urlListItem = urlListItem[1:] #: Başlangıçdaki soru işaret kaldırıldı.

                if "!" in urlListItem: #: Son liste belirleyicisi
                    x = -1
                    for i in range(3): #: Sona en fazla 3 rakam girilebilir. letterboxd'da max bulubilen liste sayısı 250
                        if urlListItem[x-1] == "!":
                            endList = int(urlListItem[x:])
                            urlListItem = urlListItem[:x-1]
                        x += -1
                else:
                    endList = 'Not specified.'
                    
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
                    print(f"{preCmdInfo}{colored('Entry info;', color='yellow')}")
                    print(f"{preCmdInfo}Query: {colored(urlListItem,'grey',attrs=['bold'])}")
                    print(f"{preCmdInfo}Last list: {colored(endList,'grey',attrs=['bold'])}")
                    print(f'{preCmdInfo}{searchMetaTitle}')
                    print(f'{preCmdInfo}{searchListsQCountMsg}')
                    print(f"{preCmdInfo}Page URL: {colored(searchLMetaUrl,'grey',attrs=['bold'])}")   
                    print(f"{preCmdInfo}Last Page: {colored(searchListsQLastsPage,'grey',attrs=['bold'])}")
                    print(subLine)
                sayfa, liste = 0, 0
                for i in range(int(searchListsQLastsPage)):
                    sayfa += 1
                    connectionPage = searchList+f'page/{sayfa}'
                    searchListDom = doReadPage(connectionPage)
                    listsUrls = searchListDom.find_all('a', attrs={'class':'list-link'}) #: Okunmuş sayfadaki tüm listelerin adresleri.
                    print(supLine)
                    print(f"{preCmdInfo}{colored('Process info;', color='yellow')}") #: Process Title
                    print(f"{preCmdInfo}CP: {colored(sayfa,'grey',attrs=['bold'])}, PL: {colored(len(listsUrls),'grey',attrs=['bold'])}, CPURL: {colored(connectionPage,'grey',attrs=['bold'])}") #: CP: Current Page, PL: Page list, CPURL: Current Page Url
                    for listsUrl in listsUrls:
                        if liste == endList:
                            print(f"{preCmdInfo}Liste sayısı belirlenen sayıya ({colored(liste,'grey',attrs=['bold'])}) ulaştı.")
                            break
                        liste += 1
                        print(f'{preCmdInfo}P{sayfa}:L{liste}')
                        urlListItem = siteDomain+listsUrl.get('href') #: https://letterboxd.com + /user_name/list/list_name
                        userListAvailable, approvedListUrl = userListCheck(doReadPage(urlListItem))
                        if approvedListUrl not in urlList:
                            if userListAvailable:
                                urlList.append(approvedListUrl)
                                print(f"{preCmdCheck}{colored('Eklendi.','green')}")
                        else:
                            print(f'{preCmdUnCheck}Bu listeyi daha önce eklemişiz.')
                            liste -= 1
                    else:
                        continue
                    print(subLine)
                    break
                break
            
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
    
    listEnterPassOff, processLoopNo = True, 0 #: For döngüne ait 
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
        if listEnterPassOff:
            listEnter = input(f"{preCmdInput}Press enter to confirm the entered information. ({cmdBlink('Enter', 'green')})")
            
            if listEnter == "":
                listEnter, autoEnterMsg = True, '[Manual]'
            elif listEnter == ".":
                listEnter, autoEnterMsg = True, '[Auto]'
                listEnterPassOff = False
                print(f'{preCmdInfo}Listeler otomatik olarak onaylanacak şekilde ayarlandı.')
            else:
                listEnter = False
                print(f"{preCmdInfo}The {colored('session was canceled','red', attrs=['dark'])} because you did not verify the information.")
                txtLog(f'{preLogInfo}The session was canceled because you did not verify the information.',logFilePath)
    
        if listEnter:
            txtLog(f'{preLogInfo}Şimdiki listeye erişim başlatılıyor.',logFilePath)
            print(f"{preCmdInfo}{colored(f'List confirmed. {autoEnterMsg}', color='green')}")
            
            lastPageNo = getListLastPageNo()
            openCsv = f'{exportsPath}{cListOwner}_{cListDomainName}_{cListRunTime}.csv' 
            dirCheck([exportsPath]) #: Export klasörünün kontrolü.
            with open(openCsv, 'w', newline='', encoding="utf-8") as csvFile: #: Konumda Export klasörü yoksa dosya oluşturmayacaktır.
                writer = csv.writer(csvFile)
                writer.writerow(["Title", "Year"]) #: Csv açıldıktan sonra en üste yazılacak başlıklar.
                
                loopCount = 1
                print(supLineFilms,end='')
                for x in range(int(lastPageNo)):
                    txtLog(f'Connecting to: {currentUrListItemDetailPage}{str(x+1)}',logFilePath)
                    currentDom = doReadPage(f'{currentUrListItemDetailPage}{str(x+1)}')
                    loopCount = doPullFilms(loopCount, currentDom)
                csvFile.close() #: Açtığımız dosyayı manuel kapattık
            
            os.system(f'title {processState} completed!')
            txtLog(f'{preLogInfo}{processState} completed!',logFilePath)
            print(f'{preCmdInfo}{loopCount-1} film {cmdBlink(openCsv,"yellow")} dosyasına aktarıldı.') #: Filmerin hangi CSV dosyasına aktarıldığı ekrana yazdırılır.
            print(subLine)
            print(f"{preCmdInfo}{colored(f'{processState} completed!', color='green')}")
            
    combineCsv()
    os.system(f'title Session: {currenSessionHash} ended!')
    print(f"{preCmdInfo}Process State: {cmdBlink(processState +' Finish.','green')}")
    print(f'{preCmdInfo}{colored(f"Session: {currenSessionHash} ended.", color="green")}')  
    txtLog(f'{preLogInfo}Session: {currenSessionHash} ended.',logFilePath)
    test_pause()
    