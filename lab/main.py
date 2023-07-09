import csv, os, glob #: PMI
from time_methods import getRunTime #: PMI
from hash_methods import getChanges #: PMI
from log_methods import errorLine #: PMI
from req_methods import doReadPage, getMetaContent, getMovieCount, getListLastPageNo, getBodyContent, doPullFilms
from os_methods import dirCheck, settingsFileSet, terminalTitle, clearTerminal, terminalEcho
from constants import * #: Constants
while True: #: Other libs
    try:
        import arrow, pandas as pd #: PMI
        from bs4 import BeautifulSoup as bs #: BeautifulSoup
        from color_methods import ced, cmdBlink, preCmdErr, preCmdInput, preCmdInfo, preCmdCheck, preCmdUnCheck, preCmdMiddleDot, preCmdMiddleDotList, supLineFilms, preBlankCount
        # from libs.termcolor110.termcolor import colored
        break
    except ImportError as e: #: Trying import
        print('Import Error: ', e)
        os.system('pipreqs --encoding utf-8 --force') #: pipreqs kullanarak kurulmasını sağlıyoruz.
        os.system('pip install -r requirements.txt & pip list') #: pip list kullanarak kurulmuş modülleri listeliyoruz.

sessionStartHash =  getRunTime() #: Generate start hash
currenSessionHash = getRunTime() #: sessionHashes = {'Startup':sessionStartHash,'Current':currenSessionHash}
hashChanges = getChanges(len(sessionStartHash),sessionStartHash,currenSessionHash)
logDirName, exportDirName = settingsFileSet() #: Set Export dir and Log dirs
logFilePath = f'{logDirName}/{currenSessionHash}.txt' #: Set log file dir
exportsPath = f'{exportDirName}/{currenSessionHash}/'

def listSignature(cListDom, processState, cListOwner, cListRunTime, cListDomainName, currentUrListItem, currentUrListItemDetail, currentUrListItemDetailPage): #: x: 0 start msg, 1 end msg
    try:
        try: ## Liste sayfasından bilgiler çekmeyi denemek.
            listBy = cListDom.select("[itemprop=name]")[0].text #: Liste sahibi ismi çekiliyor.
            listTitle = cListDom.select("[itemprop=title]")[0].text.strip() #: Liste başlığının ismini çekiliyor.
            listPublicationTime = cListDom.select(".published time")[0].text #: Liste oluşturulma tarihi çekiliyor.
            listPT = arrow.get(listPublicationTime).humanize() #: Liste oluşturulma tarihi düzenleniyor. Arrow: https://arrow.readthedocs.io/en/latest/
            listLastPage = getListLastPageNo(cListDom, currentUrListItemDetailPage) #: Liste son sayfası öğreniliyor.
            listMovieCount =  getMovieCount(listLastPage) #: Listedeki film sayısı hesaplanıyor.

            try: ## Filtre bilgilerini liste sayfasından edinmeyi denemek.
                domSelectedDecadeYear = cListDom.select(".smenu-subselected")[3].text + 'movies only was done by.' #: Liste sayfasından yıl aralık filtre bilgisi alınıyor.
                domSelectedGenre = cListDom.select(".smenu-subselected")[2].text + 'only movies.' #: Liste sayfasından tür filtre bilgisi alınıyor.
                domSelectedSortBy = cListDom.select(".smenu-subselected")[0].text + '.' #: Liste sayfasından sıralama filtre bilgisi alınıyor.
            except Exception as e: ## Filtre bilgileri edinirken bir hata oluşursa..
                # txtLog(f'{PRE_LOG_ERR}Filtre bilgileri elde bir sorun gerçekleşti.',logFilePath)
                print('Filtre bilgileri elde bir sorun gerçekleşti.')
                domSelectedDecadeYear, domSelectedGenre, domSelectedSortBy = 3*'Unknown' #: Filtre bilgileri edinemediğinde her filtreye None eklenir.

            try: ## Search list update time
                listUpdateTime = cListDom.select(".updated time")[0].text #: Liste düzenlenme vakti çekiliyor.
                listUT = arrow.get(listUpdateTime).humanize() #: Çekilen liste düzenlenme vakti okunmaya uygun hale getiriliyor.
            except Exception as e: #: Düzenleme vakti edinemezse.
                errorLine(e)
                listUT = 'No editing.' #: Hata alınırsa liste düzenlenmemiş varsayılır.
            finally: ## Kontrol sonu işlemleri.
                terminalTitle(f'{processState} Process: @{cListOwner}.')
                print(f"\n{preCmdInfo}Process State: {cmdBlink(processState,'green')}")
                print(SUP_LINE)
                print(f"{preCmdInfo}{ced('List info;', color='yellow')}")
                print(f"{preCmdMiddleDot}List by {ced(listBy,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Updated: {ced(listUT,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Published: {ced(listPT,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List title: {ced(listTitle, 'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Filters;")
                print(f"{preCmdMiddleDotList}Filtered as {ced(domSelectedDecadeYear,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDotList}Filtered as {ced(domSelectedGenre,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDotList}Movies sorted by {ced(domSelectedSortBy,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List hash: {ced(cListRunTime,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Sayfa sayısı: {ced(listLastPage,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Number of movies: {ced(listMovieCount,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List domain name: {ced(cListDomainName,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}List URL: {ced(currentUrListItem,'blue', attrs=['bold'])}")
                print(f"{preCmdMiddleDot}Process URL: {ced(currentUrListItemDetail,'blue', attrs=['bold'])}")

            #txtLog(f'{PRE_LOG_INFO}İmza yazdırma sonu.',logFilePath)
        except Exception as e:
            errorLine(e)
            #txtLog(f'{PRE_LOG_ERR}Liste bilgileri çekilirken hata.',logFilePath)
    except Exception as e: #: İmza seçimi başarısız.
        errorLine(e)
        #txtLog(f'{PRE_LOG_ERR}İmza yüklenemedi. Program yine de devam etmeyi deneyecek.',logFilePath)

def userListCheck(_url_list_item_dom, urlListItem) : #: Kullanıcının girilen şekilde bir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        try: #: meta etiketinden veri almayı dener eğer yoksa liste değil.
            metaOgType = getMetaContent(_url_list_item_dom,'og:type')

            if metaOgType == "letterboxd:list": # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşılır.
                #txtLog(f'{PRE_LOG_INFO}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {metaOgType}',logFilePath)
                metaOgUrl = getMetaContent(_url_list_item_dom,'og:url') #: Liste yönlendirmesi var mı bakıyoruz
                metaOgTitle = getMetaContent(_url_list_item_dom, 'og:title')  #: Liste ismini alıyoruz. Örnek: 'Search results for best comedy'
                bodyDataOwner = getBodyContent(_url_list_item_dom,'data-owner') #: Liste sahibinin kullanıcı ismi.
                print(f'{preCmdCheck}{ced("Found it: ", color="green")}@{ced(bodyDataOwner,"yellow")} "{ced(metaOgTitle,"yellow")}"') #: Liste sahibinin kullanıcı ismi ve liste ismi ekrana yazdırılır.

                #> Girilen URL Meta ile aynıysa..
                if urlListItem == metaOgUrl or f'{urlListItem}/' == metaOgUrl: pass #txtLog(f'{PRE_LOG_INFO}Liste adresi yönlendirme içermiyor.',logFilePath)
                else: # Girilen URL Meta ile uyuşmuyorsa..
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
                #txtLog(f'{PRE_LOG_INFO}{urlListItem} listesi bulundu: {metaOgTitle}',logFilePath)

                currentListAvaliable = True
        except Exception as e:
            errorLine(e)
            metaOgUrl = ''
            currentListAvaliable = False
    except Exception as e:
        errorLine(e)
        currentListAvaliable = False
    finally: return currentListAvaliable, metaOgUrl

def currentListDomainName(currentUrListItem):
    _f_ = '/list/'
    return currentUrListItem[currentUrListItem.index(_f_)+len(_f_):].replace('/',"")

def combineCsv(urlList): #: Birden fazla liste üzerinde çalışılıyorsa k
    if len(urlList) > 1:
        print(SUP_LINE)
        print(f"{preCmdInfo}{ced('Merge process info;', color='yellow')}")
        combineDir = f'{exportDirName}/Combined/' #: Kombine edilen listelerin barındığı klasör
        combineCsvFile = f'{currenSessionHash}_Normal-Combined.csv' #: Kombine dosyasının ismi.
        noDuplicateCsvFile = f'{currenSessionHash}_NoDuplicate-Combined.csv' #: NoDuplicate file name
        combineCsvPath = combineDir + combineCsvFile #: Kombine dosyasının yolu.
        noDuplicateCsvPath = combineDir + noDuplicateCsvFile #: NoDuplciate file path
        dirCheck([combineDir]) #: Combine dir check
        #txtLog(f'{PRE_LOG_INFO}Birden fazla liste üzerinde çalışıldığından listeler kombine edilecek.', logFilePath) #: Process logger

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
            splitCsv(noDuplicateCsvPath) # Ayıklama sonrası, aktarma ayırması gerekliyse gerçekleştiriyoruz.
        except Exception as e: pass #txtLog(f'Listeler kombine edilemedi. Hata: {e}',logFilePath) #: Process logger
        print(SUB_LINE)
    else: pass #txtLog('Tek liste üzerinde çalışıldığı için işlem kombine edilmeyecek.',logFilePath) #: Process logger

def splitCsv(split_csv_path):
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

def extractObj(job,obj):
    try:
        while job[-1] == obj: ## $job sonunda $obj olduğu sürece..
            job = job[:-1] # her defasında $job sonundan $obj siler.
    except: pass
    return job

def urlFix(x, urlList, urlListItem):
    urlListItemDom = doReadPage(x) #: Sayfa dom'u alınır.
    userListAvailable, approvedListUrl = userListCheck(urlListItemDom, urlListItem) #: Liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
    if userListAvailable and approvedListUrl not in urlList: ## Liste kullanıma uygunsa ve doğrulanmış URL daha önce URL Listesine eklenmediyse..
        urlList.append(approvedListUrl) #: Doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
    return urlList

def coloredDictPrint(colored_dict, main_title=None): # title, dict
    print(SUP_LINE)
    if main_title != None: print(f"{preCmdInfo}{ced(f'{main_title}', color='yellow')}")
    for listHeader in colored_dict:
        print(f"{preCmdMiddleDot}{ced(listHeader, attrs=['bold', 'underline'])}")
        for listHeaderItem in colored_dict[listHeader]:
            print(f"{preCmdMiddleDotList}{listHeaderItem}: {ced(colored_dict[listHeader][listHeaderItem],'blue')}")
    print(SUB_LINE)


def main():
    terminalTitle(f'Welcome %USERNAME%. & color')
    clearTerminal()

    sessionLoop = 0 #: while loop sayacı
    

    while True:
        clearTerminal() # İlk başlangıç ve yeni başlangıçlara temiz bir başlangıç.
        print(f"{preCmdInfo}Session Hash: {sessionStartHash}{'' if sessionStartHash == currenSessionHash else ' -> ' + hashChanges}") #: Her oturum başlangıcı için farklı bir isim üretildi.
        dirCheck([logDirName,exportDirName]) #: Log file check

        inputLoopNo, urlList, breakLoop, listEnterPassOn = 0, [], False, True #: While döngüne ait 
        while True:
            inputLoopNo += 1 #: Başlangıçta döngü değerini artırıyoruz.
            urlListItem = str(input(f'{preCmdInput}List URL[{inputLoopNo}]: ')).lower() #: Kullanıcıdan liste url'i alınması ve düzenlenmesi.
            if len(urlListItem) > 0: ## Giriş boş değilse..

                if urlListItem[0:len(SPLIT_PARAMETER)] == SPLIT_PARAMETER: # Split görevi.
                    splitCsv(urlListItem[len(SPLIT_PARAMETER):])
                    inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                    continue

                if '.' in urlListItem: # Girişte nokta varsa..
                    if urlListItem[-1] == '.' or urlListItem == '.': # Giriş nokta ile bitiyor veya tek nokta ise..
                        breakLoop = True #: Url alımını sonlandıracak bilgi.

                        if not urlListItem[0] == '?': print(f'{preCmdInfo}Parametre tanındı, liste alım işlemi sonlandırıldı.')

                        if urlListItem[0] == '?' or urlListItem == ".." or urlListItem[-2:] == "..": 
                            print(f'{preCmdInfo}Ek parametre tanındı, liste arama sonrası tüm listeler otomatik onaylanacak.')
                            listEnterPassOn, listEnter, autoEnterMsg = False , True, '[Auto]' # Otomatik onaylama yapacak bilgi.

                        if len(urlList) > 0: #: URL listesi boş değilse
                            print(f'{preCmdInfo}Liste arama işlemi sonlandırıldı, Toplam {len(urlList)} liste girişi yapıldı.')
                            break
                        else:
                            if not urlListItem[0] == '?':
                                try:
                                    urlListItem = urlListItem.replace('?','')
                                    urlListItem = extractObj(urlListItem,'.')
                                    urlList = urlFix(urlListItem, urlList, urlListItem)
                                    break
                                except:
                                    print(f"{preCmdInfo}To finish, you must first specify a list.") 
                                    inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                                    continue

                    urlListItem = extractObj(urlListItem,'.') #: Liste url'i parçalama.

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
                    else: endList = 'Not specified.' # Son liste için bir parametre belirtilmezse.
                    searchList = f'{SITE_DOMAIN}/search/lists/{urlListItem}/'
                    searchListPreviewDom = doReadPage(searchList)

                    searchMetaTitle = getMetaContent(searchListPreviewDom,'og:title') # getting og:title
                    searchLMetaUrl = getMetaContent(searchListPreviewDom,'og:url') #: Getting og:url

                    try: searchListsQCountMsg = searchListPreviewDom.find('h2', attrs={'class':'section-heading'}).text #: Kaç liste bulunduğu hakkında bilgi veren mesaj.
                    except AttributeError:
                        print(f"{preCmdErr}Bir etiketten 'arama karşılama mesajı' alınamadı.")
                        #txtLog(f"Bir etiketten 'arama karşılama mesajı' alınamadı. Hata Mesajı: {AttributeError}", logFilePath)
                        searchListsQCountMsg = ''

                    try:    searchListsQLastsPage = searchListPreviewDom.find_all('li',attrs={'class':'paginate-page'})[-1].text #: Son sayfayı alıyoruz.
                    except: searchListsQLastsPage = 1 #: Alınamazsa sayfada tek sayfa olduğu varsayılır.
                    finally:
                        coloredDict = {"Request": {"Query": urlListItem},
                                    "Response": {"Last list": endList,
                                                            "Last Page": searchListsQLastsPage,
                                                            "Page URL": searchLMetaUrl,
                                                            "Meta Title": searchMetaTitle,
                                                            "Meta Description": searchListsQCountMsg}}
                        coloredDictPrint(coloredDict) # print process info

                    print(f"{preCmdInfo}Starting list search..")

                    sayfa, liste = 0, 0
                    for i in range(int(searchListsQLastsPage)):
                        sayfa += 1
                        connectionPage = f'{searchList}page/{sayfa}'
                        searchListDom = doReadPage(connectionPage)
                        listsUrls = searchListDom.find_all('a', attrs={'class':'list-link'}) # okunmuş sayfadaki tüm listelerin adresleri.
                        print(SUP_LINE)
                        print(f"{preCmdInfo}{ced('Process info;', color='yellow')}") # process Title
                        print(f"{preCmdInfo}CP: {ced(sayfa,'blue')}, PL: {ced(len(listsUrls),'blue')}, CPURL: {ced(connectionPage,'blue')}") #: CP: Current Page, PL: Page list, CPURL: Current Page Url
                        for listsUrl in listsUrls:
                            if liste == endList:
                                print(f"{preCmdInfo}Liste sayısı belirlenen sayıya ({ced(liste,'blue')}) ulaştı.")
                                break
                            liste += 1
                            print(f'{preCmdInfo}P{sayfa}:L{liste}')
                            urlListItem = SITE_DOMAIN+listsUrl.get('href') #: https://letterboxd.com + /user_name/list/list_name
                            userListAvailable, approvedListUrl = userListCheck(doReadPage(urlListItem), urlListItem)
                            if approvedListUrl not in urlList:
                                if userListAvailable:
                                    urlList.append(approvedListUrl)
                                    print(f"{preCmdCheck}{ced('Eklendi.','green')}")
                            else:
                                print(f'{preCmdUnCheck}Bu listeyi daha önce eklemişiz.')
                                liste -= 1
                        else: continue
                        print(SUB_LINE)
                        break
                    break

                if '/detail' in urlListItem: urlListItem = urlListItem.replace('/detail','') # if url is detail page, remove detail part.

                urlListItemDom = doReadPage(urlListItem) # sayfa dom'u alınır.
                userListAvailable, approvedListUrl = userListCheck(urlListItemDom, urlListItem) # liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
                if userListAvailable: # liste kullanıma uygunsa..
                    if approvedListUrl not in urlList: #> doğrulanmış URL daha önce URL Listesine eklenmediyse..
                        urlList.append(approvedListUrl) # doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
                        if breakLoop: break # kullanıcı URL sonunda nokta belirttiyse.. URL alımını sonlandırıyoruz.
                    else: #> doğrulanmış URL daha önce işlem görecek URL listine eklenmiş ise..
                        print(f'{preCmdErr}You have already entered this address list.') #: URL'in daha önce girildiğini ekrana yazdırıyoruz.
                        inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
                else: #> kullanıcının girdiği URL doğrulanmazsa..
                    print(f"{preCmdInfo}You did not enter a valid url.")
                    inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
            else: #> kullanıcı genişliğe sahip bir değer girmez ise..
                print(f"{preCmdInfo}Just enter a period to move on to the next steps. You can also add it at the end of the URL.")
                inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
        print(f"{preCmdInfo}List address acquisition terminated.") # liste url alımı sona erdğinde mesaj bastırılır.

        processLoopNo = 0 # for döngüne ait 
        for currentUrListItem in urlList:
            processLoopNo += 1
            processState = f'[{processLoopNo}/{len(urlList)}]'
            currentUrListItemDetail = f'{currentUrListItem}detail/' # url'e detail eklendi.
            currentUrListItemDetailPage = f'{currentUrListItemDetail}page/' # detaylı url'e sayfa gezintisi için parametre eklendi.
            cListDom = doReadPage(currentUrListItemDetail) # şu anki liste sayfasını oku.

            try: cListOwner = getBodyContent(cListDom,'data-owner') # liste sahibini al.
            except Exception as e:
                print(f'{preCmdErr}Liste sahibi bilgisi alınamadı')
                #txtLog(f'Liste sahibi bilgisi alınamadı Hata: {e}',logFilePath)
                cListOwner = 'Unknown'
            cListDomainName = currentListDomainName(currentUrListItem) # liste domain ismini düzenleyerek alır.
            cListRunTime = getRunTime() # liste işlem vaktini al. 

            listSignature(
                cListDom,
                processState,
                cListOwner,
                cListRunTime,
                cListDomainName,
                currentUrListItem,
                currentUrListItemDetail,
                currentUrListItemDetailPage) # liste hakkında bilgiler bastırılır.

            if listEnterPassOn:
                listEnter = input(f"{preCmdInput}Press enter to confirm the entered information. ({cmdBlink('Enter', 'green')})")

                if listEnter == "": listEnter, autoEnterMsg = True, '[Manual]'
                elif listEnter == ".":
                    listEnter, autoEnterMsg = True, '[Auto]'
                    listEnterPassOn = False
                    print(f'{preCmdInfo}Listeler otomatik olarak onaylanacak şekilde ayarlandı.')
                else:
                    listEnter = False
                    print(f"{preCmdInfo}The {ced('session was canceled','red', attrs=['dark'])} because you did not verify the information.")
                    #txtLog(f'{PRE_LOG_INFO}The session was canceled because you did not verify the information.',logFilePath)

            if listEnter:
                #txtLog(f'{PRE_LOG_INFO}Şimdiki listeye erişim başlatılıyor.',logFilePath)
                print(SUP_LINE)
                print(f"{preCmdInfo}{ced(f'List confirmed. {autoEnterMsg}', color='green')}")

                lastPageNo = getListLastPageNo(cListDom, currentUrListItemDetailPage)
                openCsv = f'{exportsPath}{cListOwner}_{cListDomainName}_{cListRunTime}.csv' 
                dirCheck([exportsPath]) # export klasörünün kontrolü.
                with open(openCsv, 'w', newline='', encoding="utf-8") as csvFile: # konumda Export klasörü yoksa dosya oluşturmayacaktır.
                    writer = csv.writer(csvFile)
                    header = ['Year', 'Title', 'LetterboxdURI']
                    writer.writerow(header) # csv açıldıktan sonra en üste yazılacak başlıklar.

                    loopCount = 1
                    print(supLineFilms,end='')
                    for x in range(int(lastPageNo)): # sayfa sayısı kadar döngü oluştur.
                        #txtLog(f'{PRE_LOG_INFO}Connecting to {currentUrListItemDetailPage}{str(x+1)}', logFilePath) # sayfa numarasını log dosyasına yaz.
                        currentDom = doReadPage(f'{currentUrListItemDetailPage}{str(x+1)}') # sayfa dom'u alınır.
                        loopCount = doPullFilms(loopCount, currentDom, writer)
                    csvFile.close() # açtığımız dosyayı manuel kapattık

                terminalTitle(f'{processState} completed!') # dosya oluşturulduğunda ekrana yazı yazılır.
                #txtLog(f'{PRE_LOG_INFO}{processState} completed!', logFilePath) # dosya oluşturulduğunda log dosyasına yazı yazılır.
                print(f'{preCmdInfo}{loopCount-1} film {cmdBlink(openCsv,"yellow")} dosyasına aktarıldı.') # filmerin hangi CSV dosyasına aktarıldığı ekrana yazdırılır.
                print(SUB_LINE)
                print(f"{preCmdInfo}{ced(f'{processState} completed!', 'green')}") # işlem tamamlandığında mesajı ekrana yazdırıyoruz.

        combineCsv(urlList)

        terminalTitle(f'Session: {currenSessionHash} ended!') # terminal header
        print(f"{preCmdInfo}Process State: {cmdBlink(processState +' Finish.','green')}")
        print(f"{preCmdInfo}{ced(f'Session: {currenSessionHash} ended.', 'green')}")
        #txtLog(f'{PRE_LOG_INFO}Session: {currenSessionHash} ended.', logFilePath) # write log
        terminalEcho(f"{preCmdInfo}{cmdBlink('Press enter to continue with the new session.','yellow')} & pause >nul")

# STARTUP
if __name__ == '__main__':
    main()