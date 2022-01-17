import csv, sys, os, json #: PMI
from datetime import datetime #: PMI
from inspect import currentframe #: PMI
while True: #: Other libs
    try:
        import arrow
        import requests
        from bs4 import BeautifulSoup
        from termcolor import colored
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
                print(f'{tempLoopCount}) {movieName} ({movieYear})')
            writer.writerow([str(movieName), str(movieYear)])
            tempLoopCount += 1
        return tempLoopCount
    except Exception as e:
        if cmdLogOnOff:
            errorLine(e)  
            txtLog('An error was encountered while obtaining movie information.', logFilePath)

def doReadPage(tempUrl): #: Url'si belirtilen sayfanın okunup, dom alınması.
    try:
        txtLog(f'{preLogInfo}Trying connect to [{tempUrl}]',logFilePath)                            #: Log dosyasına bağlantı başlangıcında bilgi veriliyor.
        urlResponseCode = requests.get(tempUrl)                                         #: Get response code.
        urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')  #: Get page dom.               
        return urlDom                                                                #: Return page dom.
    except Exception as e:
        if cmdLogOnOff:
            errorLine(e)                                                                #: Dom edinirken hata gerçekleşirse..
            txtLog(f'{preLogErr}Connection to address failed [{tempUrl}]',logFilePath)

def doReset():  # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e:
        if cmdLogOnOff:
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
        if cmdLogOnOff:
            errorLine(e)                                                             
    finally:
        txtLog(f'{preLogInfo}Sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPageNo} olduğu öğrenildi.',logFilePath)
        return lastPageNo

def getMovieCount(tempLastPageNo):  # Film sayısını öğreniyoruz
    try:                                                                                                                                ## Listenin son sayfa işlemleri.
        lastPageDom = doReadPage(f'{currentUrListItemDetailPage}{tempLastPageNo}')                                                                              #: Getting lastpage dom.
        lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li") #: Sayfa kodları çekildi.
        lastPageMoviesCount =  len(lastPageArticles)                                                                                    #: Film sayısı öğrenildi.
        movieCount = ((int(tempLastPageNo)-1)*100)+lastPageMoviesCount                                                                  #: Toplam film sayısını belirlemek.
        txtLog(f"{preLogInfo}Listedeki film sayısı {movieCount} olarak bulunmuştur.",logFilePath)                                                   #: Film sayısı hesaplandıktan sonra ekrana yazdırılır.
        return movieCount                                                                                                               #: Film sayısı çağrıya gönderilir.
    except Exception as e:
        if cmdLogOnOff:
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
                if cmdLogOnOff:
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
                if cmdLogOnOff:
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
                domSelectedDecadeYear, domSelectedGenre, domSelectedSortBy = 3*'?' #: Filtre bilgileri edinemediğinde her filtreye ? eklenir.
                if cmdLogOnOff:
                    errorLine(e)                                              
                    txtLog(f'{preLogErr}Film filtre bilgileri alınamadı..',logFilePath)
            try: ## Search list update time
                listUpdateTime = cListDom.select(".updated time")[0].text #: Liste düzenlenme vakti çekiliyor.
                listUT = arrow.get(listUpdateTime).humanize() #: Çekilen liste düzenlenme vakti okunmaya uygun hale getiriliyor.
            except Exception as e: #: Düzenleme vakti edinemezse..
                if cmdLogOnOff:
                    errorLine(e)
                listUT = 'No editing.' #: Hata alınırsa liste düzenlenmemiş varsayılır.
            finally: ## Kontrol sonu işlemleri.
                print(f"\n{preCmdInfo}{cmdBlink(f'Process State : {processState}','white')}") #: İşlem durumu, sırası ekrana bastırılır.
                os.system(f'title {processState} Process: @{cListOwner}.')
                print(supLine) 
                print(f'{preCmdInfo}{colored("List info;", color="yellow")}') #: Liste başlığı.
                print(f'{preCmdMiddleDot}List by {listBy}') # Liste sahibinin görünen adı yazdırılıyor.
                print(f'{preCmdMiddleDot}List title: {listTitle}') #: Liste ismi yazdırılıyor.
                print(f'{preCmdMiddleDot}List hash: {cListRunTime}')
                print(f'{preCmdMiddleDot}List domain name: {cListDomainName}')
                print(f'{preCmdMiddleDot}Sayfa sayısı: {listLastPage}')
                print(f'{preCmdMiddleDot}Number of movies: {listMovieCount}')
                print(f'{preCmdMiddleDot}Filtered as {domSelectedDecadeYear}')
                print(f'{preCmdMiddleDot}Filtered as {domSelectedGenre}')
                print(f'{preCmdMiddleDot}Movies sorted by {domSelectedSortBy}')
                print(f'{preCmdMiddleDot}Published: {listPT}') #: or print(f'Published: {listPtime.humanize(granularity=["year","month", "day", "hour", "minute"])}')
                print(f'{preCmdMiddleDot}Updated: {listUT}')
                print(f'{preCmdMiddleDot}List URL: {currentUrListItem}')
                print(f'{preCmdMiddleDot}Process URL: {currentUrListItemDetail}') #: İşlem görecek URL ekrana bastırılır.
            log = f'{preLogInfo}İmza yazdırma sonu.' #: İmza sonu log bilgisi işlenir.
        except Exception as e:
            if cmdLogOnOff:
                errorLine(e)
                txtLog(f'{preLogErr}Liste bilgileri çekilirken hata.',logFilePath)
    except Exception as e: #: İmza seçimi başarısız.
        if cmdLogOnOff:
            errorLine(e)
        log = f'{preLogErr}İmza yüklenemedi. Program yine de devam etmeyi deneyecek.' #: İmza sonu log bilgisi işlenir.
    finally: ## Seçili imza sonunda uygulanacaklar..
        txtLog(log,logFilePath)

def userListCheck(_urlListItemDom): #: Kullanıcının girilen şekilde bir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        try: #: meta etiketinden veri almayı dener eğer yoksa liste değil.
            metaOgType = getMetaContent(_urlListItemDom,'og:type') 

            if metaOgType == "letterboxd:list": # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşılır.
                txtLog(f'{preLogInfo}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {metaOgType}',logFilePath)
                metaOgUrl = getMetaContent(_urlListItemDom,'og:url') #: Liste yönlendirmesi var mı bakıyoruz
                metaOgTitle = getMetaContent(_urlListItemDom, 'og:title')  #: Liste ismini alıyoruz.
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
            if cmdLogOnOff:
                errorLine(e)
            metaOgUrl = ''
            currentListAvaliable = False
    except Exception as e:
        if cmdLogOnOff:
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
    return f'[{colored(m,color=c)}] '

def cmdBlink(m,c):
    return colored(m,c,attrs=["blink"])

# INITIAL ASSIGNMENTS
if True:
    os.system(f'color & cls & title Welcome %USERNAME%.')
    # Domain
    siteProtocol, siteUrl = "https://", "letterboxd.com" #: Saf domain'in parçalanarak birleştirilmesi
    siteDomain = siteProtocol + siteUrl #: Saf domain'in parçalanarak birleştirilmesi
    # Cmd Pre
    preCmdMiddleDot = cmdPre(u"\u00B7","cyan") #: Cmd middle dot pre
    preCmdInput = cmdPre(">","green") #: Cmd input msg pre
    preCmdInfo = cmdPre("#","yellow") #: Cmd info msg pre
    preCmdErr = cmdPre("!","red") #: Cmd error msg pre
    preCmdCheck = cmdPre('✓','green') #: Cmd error msg pre
    preCmdUnCheck = cmdPre('X','red')
    preBlankCount = 4*' ' #: Cmd msg pre blank calc
    # Log Pre
    preLogInfo = "Info: " #: Log file ingo msg pre
    preLogErr = "Error: " #: Log file err msg pre
    # Cmd Lines
    supLine = '_'*80 #: sup line lenght
    subLine = '¯'*80 #: sub line lenght

    settingsFileName = 'settings'+'.json'

    ## Açılıp kapanabilen özellikler..
    cmdPrintFilms = True #: Cmd ekran bildirmeleri
    cmdLogOnOff = True #: Cmd ekran bildirmeleri

    if cmdPrintFilms:
        supLineFilms,subLineFilms = f'{supLine}\n{preCmdInfo}{colored("Movies on the list;", color="yellow")}\n', f'{subLine}\n'
    else:
        supLineFilms,subLineFilms = '',''

# STARTUP
sessionLoop = 0 #: While döngüne ait 
sessionStartHash =  getRunTime() #: Generate start hash
logDirName, exportDirName = settingsFileSet() #: Set Export dir and Log dir
while True:
    os.system('cls') #: İlk başlangıç ve yeni başlangıçlara temiz bir başlangıç.
    currenSessionHash = getRunTime() #: sessionHashes = {'Startup':sessionStartHash,'Current':currenSessionHash}
    hashChanges = getChanges(len(sessionStartHash),sessionStartHash,currenSessionHash)
    logFilePath = f'{logDirName}/{currenSessionHash}.txt' #: Set log file dir
    exportsPath = f'{exportDirName}/{currenSessionHash}/'
    print(f"{preCmdInfo}Session Hash: {sessionStartHash}{'' if sessionStartHash == currenSessionHash else ' -> ' + hashChanges}") #: Her oturum başlangıcı için farklı bir isim üretildi.
    dirCheck([logDirName]) #: Log file check     
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
            elif urlListItem[0] == '?': ## Giriş başlangıcında soru işareti varsa.. (Liste arama moduna geçilir.)
                print(f'{preCmdInfo}Parameter recognized, searching list.')
                urlListItem = urlListItem[1:] #: Başlangıçdaki soru işaret kaldırıldı.
                searchList = f'https://letterboxd.com/search/lists/{urlListItem}/'
                ## Getting
                searchListPreviewDom = doReadPage(searchList)
                searchMetaTitle = getMetaContent(searchListPreviewDom,'og:title')
                searchLMetaUrl = getMetaContent(searchListPreviewDom,'og:url')
                searchListsQCountMsg = searchListPreviewDom.find('h2', attrs={'class':'section-heading'}).text #: Kaç liste bulunduğu hakkında bilgi veren mesajı çekiyoruz.
                try:
                    searchListsQLastsPage = searchListPreviewDom.find_all('li',attrs={'class':'paginate-page'})[-1].text #: Son sayfayı alıyoruz.
                except:
                    searchListsQLastsPage = 1 #: Alınamazsa sayfada tek sayfa olduğu varsayılır.
                finally:
                    print(f'{preCmdInfo}{searchMetaTitle}')
                    print(f'{preCmdInfo}{searchListsQCountMsg}')
                    print(f'{preCmdInfo}Page URL: {searchLMetaUrl}')   
                    print(f'{preCmdInfo}Last Page: {searchListsQLastsPage}')

                sayfa, liste = 0, 0
                for i in range(int(searchListsQLastsPage)):
                    sayfa += 1
                    connectionPage = searchList+f'page/{sayfa}'
                    print(f'{preCmdInfo}Bağlanılan sayfa: {connectionPage}')
                    searchListDom = doReadPage(connectionPage)
                    listsUrls = searchListDom.find_all('a', attrs={'class':'list-link'}) #: Okunmuş sayfadaki tüm listelerin adresleri.
                    print(f'{preCmdInfo}Current Page: {sayfa}, Current page lists: {len(listsUrls)}')
                    for listsUrl in listsUrls:
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
        processState = f'[{len(urlList)}/{processLoopNo}]'
        currentUrListItemDetail = f'{currentUrListItem}detail/' # Url'e detail eklendi.
        currentUrListItemDetailPage = f'{currentUrListItemDetail}page/' #: Detaylı url'e sayfa gezintisi için parametre eklendi.
        cListDom = doReadPage(currentUrListItemDetail) #: Şu anki liste sayfasını oku.
        cListOwner = getBodyContent(cListDom,'data-owner') #: Liste sahibini al.
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
                print(preCmdInfo,f"The {colored('session was canceled','red')} because you did not verify the information.")
                txtLog(f'{preLogInfo}The session was canceled because you did not verify the information.',logFilePath)
    
        print(subLine)
        if listEnter:
            txtLog(f'{preLogInfo}Şimdiki listeye erişim başlatılıyor.',logFilePath)
            dirCheck([exportsPath]) #: Export klasörünün kontrolü.
            openCsv = f'{exportsPath}{cListOwner}_{cListDomainName}_{cListRunTime}.csv' 
            print(f"{preCmdInfo}{colored(f'List confirmed. {autoEnterMsg}', color='green')}")
            lastPageNo = getListLastPageNo()
            
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
                print(subLineFilms,end='') #: İşlem bitimi sonrası alt çizgi. (Alt çizgi için üst çizgi kullanılır.)
            
            os.system(f'title {processState} completed!')
            print(f"{preCmdInfo}{colored(f'{processState} completed!', color='green')}")  
            txtLog(f'{preLogInfo}{processState} completed!',logFilePath)
            print(f'{preCmdInfo}{loopCount-1} film {cmdBlink(openCsv,"yellow")} dosyasına aktarıldı.') #: Filmerin hangi CSV dosyasına aktarıldığı ekrana yazdırılır.
            
    os.system(f'title Session: {currenSessionHash} ended!')
    print(f'{preCmdInfo}{colored(f"Session: {currenSessionHash} ended.", color="green")}')  
    txtLog(f'{preLogInfo}Session: {currenSessionHash} ended.',logFilePath)
    test_pause()
    