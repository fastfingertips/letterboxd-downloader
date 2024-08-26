from termcolor import colored as ced
import csv

# -- Local Imports -- #

from utils.request import fetch_page_dom

from utils.url.custom import fix_url
from utils.dom.custom import extract_and_write_films
from utils.set.custom import readSettings
from utils.time.custom import get_run_time
from utils.dict.custom import listSignature
from utils.log.custom import startLog, txtLog
from utils.csv.custom import combineCsv, splitCsv
from utils.session.custom import startSession, endSession
from utils.file.custom import ensure_files_exist, ensure_directories_exist

from utils.cmd_format import cmd_blink
from utils.cmd_display import coloredDictPrint
from utils.hash_utils import getChanges, extractObj
from utils.terminal import execute_terminal_command, set_terminal_title
from utils.dom_utils import (
  get_list_last_page_no,
  get_meta_content,
  get_body_content,
  check_user_list
)

from constants.project import (
    DEFAULT_EXPORT_KEY,
    SPLIT_PARAMETER,
    DEFAULT_LOG_KEY,
    PRE_LOG_INFO,
    SITE_DOMAIN,
    SUB_LINE,
    SUP_LINE
)

from constants.terminal import (
    PRE_CMD_UNCHECK,
    SUP_LINE_FILMS,
    PRE_CMD_INPUT,
    PRE_CMD_CHECK,
    PRE_CMD_INFO,
    PRE_CMD_ERR
)

# -- MAIN -- #

def currentListDomainName(currentUrListItem):
    _f_ = '/list/'
    return currentUrListItem[currentUrListItem.index(_f_)+len(_f_):].replace('/',"")

# system color start end reset
# user welcome message and screen clear
execute_terminal_command(f'color & title Welcome %USERNAME%. & cls')

sessionStartHash =  get_run_time() # generate process hash
pLoop = 0 # program loop
while True:
    # STARTUP
    sessionCurrentHash = sessionStartHash if pLoop == 0 else get_run_time() # generate process hash
    startSession(sessionCurrentHash)
    startLog(sessionCurrentHash)
    pLoop += 1

    # SETTINGS
    settings = readSettings()
    logDirName = settings[DEFAULT_LOG_KEY]
    exportDirName = settings[DEFAULT_EXPORT_KEY]
    ensure_directories_exist([logDirName, exportDirName]) # check directories

    exportsPath = ''.join([exportDirName, '/', sessionCurrentHash, '/']) # exports/000000000/

    #> every session has a different name for the start.
    hashChanges = getChanges(sessionStartHash, sessionCurrentHash)
    print(f"{PRE_CMD_INFO}Session Hash: {sessionStartHash}{'' if sessionStartHash == sessionCurrentHash else ' -> ' + hashChanges}") 

    #> while initializing
    listEnterPassOn = True
    breakLoop = False
    inputLoopNo = 0
    urlList = []
    while True:
        inputLoopNo += 1 #: Başlangıçta döngü değerini artırıyoruz.
        urlListItem = str(input(f'{PRE_CMD_INPUT}List URL[{inputLoopNo}]: ')).lower() #: Kullanıcıdan liste url'i alınması ve düzenlenmesi.
        if len(urlListItem) > 0: ## Giriş boş değilse..

            #> input starts with split parameter
            if urlListItem[0:len(SPLIT_PARAMETER)] == SPLIT_PARAMETER: 
                splitCsv(urlListItem[len(SPLIT_PARAMETER):], exportDirName, sessionCurrentHash)
                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                continue

            if urlListItem[-1] == '.' and urlListItem[0] != '?':
                if not inputLoopNo > 1:
                    print(f"{PRE_CMD_INFO}To finish, you must first specify a list.") 
                    inputLoopNo -= 1
                    continue

            if '.' in urlListItem: # Girişte nokta varsa..
                if urlListItem[-1] == '.' or urlListItem == '.': # Giriş nokta ile bitiyor veya tek nokta ise..
                    breakLoop = True #: Url alımını sonlandıracak bilgi.

                    if not urlListItem[0] == '?': print(f'{PRE_CMD_INFO}Parametre tanındı, liste alım işlemi sonlandırıldı.')

                    if urlListItem[0] == '?' or urlListItem == ".." or urlListItem[-2:] == "..": 
                        print(f'{PRE_CMD_INFO}Ek parametre tanındı, liste arama sonrası tüm listeler otomatik onaylanacak.')
                        listEnterPassOn, listEnter, autoEnterMsg = False , True, '[Auto]' # Otomatik onaylama yapacak bilgi.

                    if len(urlList) > 0: #: URL listesi boş değilse
                        print(f'{PRE_CMD_INFO}Liste arama işlemi sonlandırıldı, Toplam {len(urlList)} liste girişi yapıldı.')
                        break
                    else:
                        if not urlListItem[0] == '?':
                            try:
                                urlListItem = urlListItem.replace('?','')
                                urlListItem = extractObj(urlListItem,'.')
                                urlList = fix_url(urlListItem, urlList)
                                break
                            except:
                                print(f"{PRE_CMD_INFO}To finish, you must first specify a list.") 
                                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                                continue

                urlListItem = extractObj(urlListItem,'.') #: Liste url'i parçalama.

            if urlListItem[0] == '?': 
                print(f'{PRE_CMD_INFO}Paremetre tanındı: Liste arama modu.')
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
                searchListPreviewDom = fetch_page_dom(searchList)

                searchMetaTitle = get_meta_content(searchListPreviewDom,'og:title') # getting og:title
                searchLMetaUrl = get_meta_content(searchListPreviewDom,'og:url') #: Getting og:url

                try: searchListsQCountMsg = searchListPreviewDom.find('h2', attrs={'class':'section-heading'}).text #: Kaç liste bulunduğu hakkında bilgi veren mesaj.
                except AttributeError:
                    print(f"{PRE_CMD_ERR}Bir etiketten 'arama karşılama mesajı' alınamadı.")
                    txtLog(f"Bir etiketten 'arama karşılama mesajı' alınamadı. Hata Mesajı: {AttributeError}")
                    searchListsQCountMsg = ''

                try:    searchListsQLastsPage = searchListPreviewDom.find_all('li',attrs={'class':'paginate-page'})[-1].text #: Son sayfayı alıyoruz.
                except: searchListsQLastsPage = 1 #: Alınamazsa sayfada tek sayfa olduğu varsayılır.
                finally:
                    coloredDict = {
                    "Request": {
                        "Query": urlListItem},
                    "Response": {
                        "Last list": endList,
                        "Last Page": searchListsQLastsPage,
                        "Page URL": searchLMetaUrl,
                        "Meta Title": searchMetaTitle,
                        "Meta Description": searchListsQCountMsg
                        }
                    }
                    coloredDictPrint(coloredDict) # print process info

                print(f"{PRE_CMD_INFO}Starting list search..")

                sayfa, liste = 0, 0
                for i in range(int(searchListsQLastsPage)):
                    sayfa += 1
                    connectionPage = f'{searchList}page/{sayfa}'
                    searchListDom = fetch_page_dom(connectionPage)
                    listsUrls = searchListDom.find_all('a', attrs={'class':'list-link'}) # okunmuş sayfadaki tüm listelerin adresleri.

                    queryPage = {
                        "Process": {
                            "Current Page": sayfa,
                            "Page URL": connectionPage,
                            "Lists Count": len(listsUrls)
                        }
                    }

                    coloredDictPrint(queryPage)
                    for listsUrl in listsUrls:
                        if liste == endList:
                            print(f"{PRE_CMD_INFO}Liste sayısı belirlenen sayıya ({ced(liste,'blue')}) ulaştı.")
                            break
                        liste += 1
                        print(f'{PRE_CMD_INFO}List page/rank: {ced(sayfa, "blue")}/{ced(liste, "blue")}')
                        urlListItem = SITE_DOMAIN+listsUrl.get('href') #: https://letterboxd.com + /user_name/list/list_name
                        userListAvailable, approvedListUrl = check_user_list(fetch_page_dom(urlListItem), urlListItem)
                        if approvedListUrl not in urlList:
                            if userListAvailable:
                                urlList.append(approvedListUrl)
                                print(f"{PRE_CMD_CHECK}{ced('Eklendi.','green')}")
                        else:
                            print(f'{PRE_CMD_UNCHECK}Bu listeyi daha önce eklemişiz.')
                            liste -= 1
                    else: continue
                    print(SUB_LINE)
                    break
                break

            if '/detail' in urlListItem: urlListItem = urlListItem.replace('/detail','') # if url is detail page, remove detail part.

            urlListItemDom = fetch_page_dom(urlListItem) # sayfa dom'u alınır.
            userListAvailable, approvedListUrl = check_user_list(urlListItemDom, urlListItem) # liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
            if userListAvailable: # liste kullanıma uygunsa..
                if approvedListUrl not in urlList: #> doğrulanmış URL daha önce URL Listesine eklenmediyse..
                    urlList.append(approvedListUrl) # doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
                    if breakLoop: break # kullanıcı URL sonunda nokta belirttiyse.. URL alımını sonlandırıyoruz.
                else: #> doğrulanmış URL daha önce işlem görecek URL listine eklenmiş ise..
                    print(f'{PRE_CMD_ERR}You have already entered this address list.') #: URL'in daha önce girildiğini ekrana yazdırıyoruz.
                    inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
            else: #> kullanıcının girdiği URL doğrulanmazsa..
                print(f"{PRE_CMD_INFO}You did not enter a valid url.")
                inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
        else: #> kullanıcı genişliğe sahip bir değer girmez ise..
            print(f"{PRE_CMD_INFO}Just enter a period to move on to the next steps. You can also add it at the end of the URL.")
            inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
    print(f"{PRE_CMD_INFO}List address acquisition terminated.") # liste url alımı sona erdğinde mesaj bastırılır.

    processLoopNo = 0 # for döngüne ait 
    for currentUrListItem in urlList:
        processLoopNo += 1
        processState = f'[{processLoopNo}/{len(urlList)}]'
        currentUrListItemDetail = f'{currentUrListItem}detail/' # url'e detail eklendi.
        currentUrListItemDetailPage = f'{currentUrListItemDetail}page/' # detaylı url'e sayfa gezintisi için parametre eklendi.
        cListDom = fetch_page_dom(currentUrListItemDetail) # şu anki liste sayfasını oku.

        try: cListOwner = get_body_content(cListDom,'data-owner') # liste sahibini al.
        except Exception as e:
            print(f'{PRE_CMD_ERR}Liste sahibi bilgisi alınamadı')
            txtLog(f'Liste sahibi bilgisi alınamadı Hata: {e}')
            cListOwner = 'Unknown'
        cListDomainName = currentListDomainName(currentUrListItem) # liste domain ismini düzenleyerek alır.
        cListRunTime = get_run_time() # liste işlem vaktini al. 

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
            listEnter = input(f"{PRE_CMD_INPUT}Press enter to confirm the entered information. ({cmd_blink('Enter', 'green')})")

            if listEnter == "": listEnter, autoEnterMsg = True, '[Manual]'
            elif listEnter == ".":
                listEnter, autoEnterMsg = True, '[Auto]'
                listEnterPassOn = False
                print(f'{PRE_CMD_INFO}Listeler otomatik olarak onaylanacak şekilde ayarlandı.')
            else:
                listEnter = False
                print(f"{PRE_CMD_INFO}The {ced('session was canceled','red', attrs=['dark'])} because you did not verify the information.")
                txtLog(f'{PRE_LOG_INFO}The session was canceled because you did not verify the information.')

        if listEnter:
            txtLog(f'{PRE_LOG_INFO}Şimdiki listeye erişim başlatılıyor.')
            print(SUP_LINE)
            print(f"{PRE_CMD_INFO}{ced(f'List confirmed. {autoEnterMsg}', color='green')}")

            lastPageNo = get_list_last_page_no(cListDom, currentUrListItemDetailPage)
            openCsv = ''.join([exportsPath, cListOwner, '_', cListDomainName, '_', cListRunTime, '.csv'])
            ensure_directories_exist([exportsPath]) # export klasörünün kontrolü.
            ensure_files_exist([openCsv]) # csv dosyasının kontrolü.

            with open(openCsv, 'w', newline='', encoding="utf-8") as csvFile: # konumda Export klasörü yoksa dosya oluşturmayacaktır.
                writer = csv.writer(csvFile)
                header = ['Year', 'Title', 'LetterboxdURI']
                writer.writerow(header) # csv açıldıktan sonra en üste yazılacak başlıklar.

                loopCount = 1
                print(SUP_LINE_FILMS, end='')
                for x in range(int(lastPageNo)): # sayfa sayısı kadar döngü oluştur.
                    txtLog(f'{PRE_LOG_INFO}Connecting to {currentUrListItemDetailPage}{str(x+1)}') # sayfa numarasını log dosyasına yaz.
                    currentDom = fetch_page_dom(f'{currentUrListItemDetailPage}{str(x+1)}') # sayfa dom'u alınır.
                    loopCount = extract_and_write_films(loopCount, currentDom, writer) # filmleri al.
                csvFile.close() # açtığımız dosyayı manuel kapattık

            # process end
            set_terminal_title(f'{processState} completed!') # change title
            print(f'{PRE_CMD_INFO}{loopCount-1} film {cmd_blink(openCsv,"yellow")} dosyasına aktarıldı.') # print info
            print(f"{PRE_CMD_INFO}{ced(f'{processState} completed!', 'green')}") # print info
            txtLog(f'{PRE_LOG_INFO}{processState} completed!') # log info
            print(SUB_LINE)

    combineCsv(urlList, exportDirName, sessionCurrentHash, exportsPath) # merge csv files

    # session end
    endSession(sessionCurrentHash)
    set_terminal_title(f'Session: {sessionCurrentHash} ended!') # change title
    print(f"{PRE_CMD_INFO}{ced(f'Session: {sessionCurrentHash} ended.', 'green')}") # print info
    txtLog(f'{PRE_LOG_INFO}Session: {sessionCurrentHash} ended.') # log info

    # process end
    print(f"{PRE_CMD_INFO}Process State: {cmd_blink(processState +' Finish.','green')}")
    execute_terminal_command(f"echo {PRE_CMD_INFO}{cmd_blink('Press enter to continue with the new session.','yellow')} & pause >nul")