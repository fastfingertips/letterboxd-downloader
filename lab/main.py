

from methods.color_ import ced, cmdBlink, coloredDictPrint, preCmdInfo, preCmdInput, preCmdErr, preCmdCheck, preCmdUnCheck, SUP_LINE, SUB_LINE, supLineFilms #: PMI
from methods.req_ import urlFix, doReadPage, getMetaContent, userListCheck, getBodyContent, listSignature, getListLastPageNo, doPullFilms
from methods.system_ import dirCheck, fileCheck, terminalSystem, terminalTitle
from methods.csv_ import splitCsv, combineCsv
from methods.session_ import startSession, endSession
from methods.time_ import getRunTime #: PMI
from methods.log_ import txtLog, startLog, readSettings
from methods.hash_ import getChanges, extractObj
from constants.project import SITE_DOMAIN, PRE_LOG_INFO, SPLIT_PARAMETER, DEFAULT_EXPORT_KEY, DEFAULT_LOG_KEY
# ---
import csv
while True: #: Other libs
    try:
        # from libs.termcolor110.termcolor import colored
        break
    except ImportError as e: #: Trying import
        print('Import Error: ', e)
        terminalSystem('pipreqs --encoding utf-8 --force') #: pipreqs kullanarak kurulmasını sağlıyoruz.
        terminalSystem('pip install -r requirements.txt & pip list') #: pip list kullanarak kurulmuş modülleri listeliyoruz.

def currentListDomainName(currentUrListItem):
    _f_ = '/list/'
    return currentUrListItem[currentUrListItem.index(_f_)+len(_f_):].replace('/',"")

# system color start end reset
# user welcome message and screen clear
terminalSystem(f'color & title Welcome %USERNAME%. & cls')

sessionStartHash =  getRunTime() # generate process hash
pLoop = 0 # program loop
while True:
    # STARTUP
    sessionCurrentHash = sessionStartHash if pLoop == 0 else getRunTime() # generate process hash
    startSession(sessionCurrentHash)
    startLog(sessionCurrentHash)
    pLoop += 1

    # SETTINGS
    settings = readSettings()
    logDirName, exportDirName = settings[DEFAULT_LOG_KEY], settings[DEFAULT_EXPORT_KEY]
    exportsPath = ''.join([exportDirName, '/', sessionCurrentHash, '/']) # exports/000000000/

    dirCheck([logDirName, exportDirName]) #: Log file check

    hashChanges = getChanges(len(sessionStartHash), sessionStartHash, sessionCurrentHash)
    print(f"{preCmdInfo}Session Hash: {sessionStartHash}{'' if sessionStartHash == sessionCurrentHash else ' -> ' + hashChanges}") #: Her oturum başlangıcı için farklı bir isim üretildi.

    inputLoopNo, urlList, breakLoop, listEnterPassOn = 0, [], False, True #: While döngüne ait 
    while True:
        inputLoopNo += 1 #: Başlangıçta döngü değerini artırıyoruz.
        urlListItem = str(input(f'{preCmdInput}List URL[{inputLoopNo}]: ')).lower() #: Kullanıcıdan liste url'i alınması ve düzenlenmesi.
        if len(urlListItem) > 0: ## Giriş boş değilse..

            if urlListItem[0:len(SPLIT_PARAMETER)] == SPLIT_PARAMETER: # Split görevi.
                splitCsv(urlListItem[len(SPLIT_PARAMETER):], exportDirName, sessionCurrentHash)
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
                                urlList = urlFix(urlListItem, urlList)
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
                    txtLog(f"Bir etiketten 'arama karşılama mesajı' alınamadı. Hata Mesajı: {AttributeError}")
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
            txtLog(f'Liste sahibi bilgisi alınamadı Hata: {e}')
            cListOwner = 'Unknown'
        cListDomainName = currentListDomainName(currentUrListItem) # liste domain ismini düzenleyerek alır.
        cListRunTime = getRunTime() # liste işlem vaktini al. 

        listDict = {
            "list_detail_page": currentUrListItemDetailPage, # https://letterboxd.com/{un}/list/{ln}/detail/page/
            "list_detail_url": currentUrListItemDetail, # https://letterboxd.com/{un}/list/{ln}/detail/
            "list_domain_name": cListDomainName, # {ln}
            "process_state": processState, #  [1/1]
            "list_run_time": cListRunTime, # 14072023022401
            "list_url": currentUrListItem, # https://letterboxd.com/{un}/list/{ln}
            "list_owner": cListOwner, # {un}
            "list_dom": cListDom # <html>...</html>
        }

        listSignature(listDict) # liste hakkında bilgiler bastırılır.

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
                txtLog(f'{PRE_LOG_INFO}The session was canceled because you did not verify the information.')

        if listEnter:
            txtLog(f'{PRE_LOG_INFO}Şimdiki listeye erişim başlatılıyor.')
            print(SUP_LINE)
            print(f"{preCmdInfo}{ced(f'List confirmed. {autoEnterMsg}', color='green')}")

            lastPageNo = getListLastPageNo(cListDom, currentUrListItemDetailPage)
            openCsv = ''.join([exportsPath, cListOwner, '_', cListDomainName, '_', cListRunTime, '.csv'])
            dirCheck([exportsPath]) # export klasörünün kontrolü.
            fileCheck([openCsv]) # csv dosyasının kontrolü.

            with open(openCsv, 'w', newline='', encoding="utf-8") as csvFile: # konumda Export klasörü yoksa dosya oluşturmayacaktır.
                writer = csv.writer(csvFile)
                header = ['Year', 'Title', 'LetterboxdURI']
                writer.writerow(header) # csv açıldıktan sonra en üste yazılacak başlıklar.

                loopCount = 1
                print(supLineFilms,end='')
                for x in range(int(lastPageNo)): # sayfa sayısı kadar döngü oluştur.
                    txtLog(f'{PRE_LOG_INFO}Connecting to {currentUrListItemDetailPage}{str(x+1)}') # sayfa numarasını log dosyasına yaz.
                    currentDom = doReadPage(f'{currentUrListItemDetailPage}{str(x+1)}') # sayfa dom'u alınır.
                    loopCount = doPullFilms(loopCount, currentDom, writer) # filmleri al.
                csvFile.close() # açtığımız dosyayı manuel kapattık

            # process end
            terminalTitle(f'{processState} completed!') # change title
            print(f'{preCmdInfo}{loopCount-1} film {cmdBlink(openCsv,"yellow")} dosyasına aktarıldı.') # print info
            print(f"{preCmdInfo}{ced(f'{processState} completed!', 'green')}") # print info
            txtLog(f'{PRE_LOG_INFO}{processState} completed!') # log info
            print(SUB_LINE)

    combineCsv(urlList, exportDirName, sessionCurrentHash, exportsPath) # merge csv files

    # session end
    endSession(sessionCurrentHash)
    terminalTitle(f'Session: {sessionCurrentHash} ended!') # change title
    print(f"{preCmdInfo}{ced(f'Session: {sessionCurrentHash} ended.', 'green')}") # print info
    txtLog(f'{PRE_LOG_INFO}Session: {sessionCurrentHash} ended.') # log info

    # process end
    print(f"{preCmdInfo}Process State: {cmdBlink(processState +' Finish.','green')}")
    terminalSystem(f"echo {preCmdInfo}{cmdBlink('Press enter to continue with the new session.','yellow')} & pause >nul")