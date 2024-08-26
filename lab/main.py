import csv

# -- Local Imports -- #

from utils.request import fetch_page_dom

from utils.terminal import execute_terminal_command, set_terminal_title

from utils.set.custom import readSettings
from utils.time.custom import get_run_time
from utils.dict.custom import listSignature
from utils.log.custom import startLog, txtLog
from utils.csv.custom import combineCsv, splitCsv
from utils.dom.custom import extract_and_write_films
from utils.session.custom import startSession, endSession
from utils.url.custom import fix_url, extract_list_domain_name
from utils.text.custom import highlight_changes, trim_end, remove_substring
from utils.file.custom import ensure_files_exist, ensure_directories_exist
from utils.color.custom import colored, print_colored_dict, blink_text
from utils.dom.custom import (
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
    ICON_UNCHECK,
    ICON_INPUT,
    ICON_CHECK,
    ICON_ERROR,
    ICON_INFO,
    SUP_LINE_FILMS
)

# -- MAIN -- #

# system color start end reset
# user welcome message and screen clear
execute_terminal_command(f'color & title Welcome %USERNAME%. & cls')

session_start_hash = get_run_time()
program_loop = 0
while True:
    # STARTUP
    session_current_hash = get_run_time() if program_loop else session_start_hash
    startSession(session_current_hash)
    startLog(session_current_hash)
    program_loop += 1

    # SETTINGS
    settings = readSettings()
    log_directory_name = settings[DEFAULT_LOG_KEY]
    export_directory_name = settings[DEFAULT_EXPORT_KEY]
    # Check directories
    ensure_directories_exist([log_directory_name, export_directory_name])
    # exports/000000000/
    exports_path = ''.join([export_directory_name, '/', session_current_hash, '/']) 

    #> every session has a different name for the start.
    hashChanges = highlight_changes(session_start_hash, session_current_hash)
    print(f"{ICON_INFO}Session Hash: {session_start_hash}{'' if session_start_hash == session_current_hash else ' -> ' + hashChanges}") 

    #> while initializing
    listEnterPassOn = True
    breakLoop = False
    inputLoopNo = 0
    url_list = []
    while True:
        inputLoopNo += 1 #: Başlangıçta döngü değerini artırıyoruz.
        url_list_item = str(input(f'{ICON_INPUT}List URL[{inputLoopNo}]: ')).lower() #: Kullanıcıdan liste url'i alınması ve düzenlenmesi.
        if len(url_list_item) > 0: ## Giriş boş değilse..

            #> input starts with split parameter
            if url_list_item[0:len(SPLIT_PARAMETER)] == SPLIT_PARAMETER: 
                splitCsv(url_list_item[len(SPLIT_PARAMETER):], export_directory_name, session_current_hash)
                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                continue

            if url_list_item[-1] == '.' and url_list_item[0] != '?':
                if not inputLoopNo > 1:
                    print(f"{ICON_INFO}To finish, you must first specify a list.") 
                    inputLoopNo -= 1
                    continue

            if '.' in url_list_item: # Girişte nokta varsa..
                if url_list_item[-1] == '.' or url_list_item == '.': # Giriş nokta ile bitiyor veya tek nokta ise..
                    breakLoop = True #: Url alımını sonlandıracak bilgi.

                    if not url_list_item[0] == '?': print(f'{ICON_INFO}Parametre tanındı, liste alım işlemi sonlandırıldı.')

                    if url_list_item[0] == '?' or url_list_item == ".." or url_list_item[-2:] == "..": 
                        print(f'{ICON_INFO}Ek parametre tanındı, liste arama sonrası tüm listeler otomatik onaylanacak.')
                        listEnterPassOn, listEnter, autoEnterMsg = False , True, '[Auto]' # Otomatik onaylama yapacak bilgi.

                    if len(url_list) > 0: #: URL listesi boş değilse
                        print(f'{ICON_INFO}Liste arama işlemi sonlandırıldı, Toplam {len(url_list)} liste girişi yapıldı.')
                        break
                    else:
                        if not url_list_item[0] == '?':
                            try:
                                url_list_item = url_list_item.replace('?','')
                                url_list_item = trim_end(url_list_item,'.')
                                url_list = fix_url(url_list_item, url_list)
                                break
                            except:
                                print(f"{ICON_INFO}To finish, you must first specify a list.") 
                                inputLoopNo -= 1 #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
                                continue

                url_list_item = trim_end(url_list_item, '.') #: Liste url'i parçalama.

            if url_list_item[0] == '?': 
                print(f'{ICON_INFO}Paremetre tanındı: Liste arama modu.')
                url_list_item = url_list_item[1:] #: Başlangıçdaki soru işaret kaldırıldı.

                if "!" in url_list_item: #: Son liste belirleyicisi
                    x = -1
                    for i in range(3): #: Sona en fazla 3 rakam girilebilir. letterboxd'da max bulubilen liste sayısı 250
                        if url_list_item[x-1] == "!":
                            endList = int(url_list_item[x:])
                            url_list_item = url_list_item[:x-1]
                        x += -1
                else: endList = 'Not specified.' # Son liste için bir parametre belirtilmezse.
                searchList = f'{SITE_DOMAIN}/search/lists/{url_list_item}/'
                searchListPreviewDom = fetch_page_dom(searchList)

                searchMetaTitle = get_meta_content(searchListPreviewDom,'og:title') # getting og:title
                searchLMetaUrl = get_meta_content(searchListPreviewDom,'og:url') #: Getting og:url

                try:
                    searchListsQCountMsg = searchListPreviewDom.find('h2', attrs={'class':'section-heading'}).text #: Kaç liste bulunduğu hakkında bilgi veren mesaj.
                except AttributeError:
                    print(f"{ICON_ERROR}Bir etiketten 'arama karşılama mesajı' alınamadı.")
                    txtLog(f"Bir etiketten 'arama karşılama mesajı' alınamadı. Hata Mesajı: {AttributeError}")
                    searchListsQCountMsg = ''

                try:
                    searchListsQLastsPage = searchListPreviewDom.find_all('li',attrs={'class':'paginate-page'})[-1].text #: Son sayfayı alıyoruz.
                except:
                    searchListsQLastsPage = 1 #: Alınamazsa sayfada tek sayfa olduğu varsayılır.
                finally:
                    # Request response summary
                    print_colored_dict({
                    "Request": {
                        "Query": url_list_item},
                    "Response": {
                        "Last list": endList,
                        "Last Page": searchListsQLastsPage,
                        "Page URL": searchLMetaUrl,
                        "Meta Title": searchMetaTitle,
                        "Meta Description": searchListsQCountMsg
                        }
                    })

                print(f"{ICON_INFO}Starting list search..")

                sayfa, liste = 0, 0
                for i in range(int(searchListsQLastsPage)):
                    sayfa += 1
                    connectionPage = f'{searchList}page/{sayfa}'
                    searchListDom = fetch_page_dom(connectionPage)
                    listsUrls = searchListDom.find_all('a', attrs={'class':'list-link'}) # okunmuş sayfadaki tüm listelerin adresleri.

                    # Query page summary
                    print_colored_dict({
                        "Process": {
                            "Current Page": sayfa,
                            "Page URL": connectionPage,
                            "Lists Count": len(listsUrls)
                        }
                    })

                    for listsUrl in listsUrls:
                        if liste == endList:
                            print(f"{ICON_INFO}Liste sayısı belirlenen sayıya ({colored(liste,'blue')}) ulaştı.")
                            break
                        liste += 1
                        print(f'{ICON_INFO}List page/rank: {colored(sayfa, "blue")}/{colored(liste, "blue")}')
                        url_list_item = SITE_DOMAIN+listsUrl.get('href') #: https://letterboxd.com + /user_name/list/list_name
                        userListAvailable, approvedListUrl = check_user_list(fetch_page_dom(url_list_item), url_list_item)
                        if approvedListUrl not in url_list:
                            if userListAvailable:
                                url_list.append(approvedListUrl)
                                print(f"{ICON_CHECK}{colored('Eklendi.','green')}")
                        else:
                            print(f'{ICON_UNCHECK}Bu listeyi daha önce eklemişiz.')
                            liste -= 1
                    else: continue
                    print(SUB_LINE)
                    break
                break
            
            # if url is detail page, remove detail part.
            url_list_item = remove_substring(url_list_item, '/detail') 

            urlListItemDom = fetch_page_dom(url_list_item) # sayfa dom'u alınır.
            userListAvailable, approvedListUrl = check_user_list(urlListItemDom, url_list_item) # liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
            if userListAvailable: # liste kullanıma uygunsa..
                if approvedListUrl not in url_list: #> doğrulanmış URL daha önce URL Listesine eklenmediyse..
                    url_list.append(approvedListUrl) # doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
                    if breakLoop: break # kullanıcı URL sonunda nokta belirttiyse.. URL alımını sonlandırıyoruz.
                else: #> doğrulanmış URL daha önce işlem görecek URL listine eklenmiş ise..
                    print(f'{ICON_ERROR}You have already entered this address list.') #: URL'in daha önce girildiğini ekrana yazdırıyoruz.
                    inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
            else: #> kullanıcının girdiği URL doğrulanmazsa..
                print(f"{ICON_INFO}You did not enter a valid url.")
                inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
        else: #> kullanıcı genişliğe sahip bir değer girmez ise..
            print(f"{ICON_INFO}Just enter a period to move on to the next steps. You can also add it at the end of the URL.")
            inputLoopNo -= 1 # başarısız girişlerde döngü sayısının normale çevrilmesi.
    print(f"{ICON_INFO}List address acquisition terminated.") # liste url alımı sona erdğinde mesaj bastırılır.

    processLoopNo = 0 # for döngüne ait 
    for currentUrListItem in url_list:
        processLoopNo += 1
        processState = f'[{processLoopNo}/{len(url_list)}]'
        currentUrListItemDetail = f'{currentUrListItem}detail/' # url'e detail eklendi.
        currentUrListItemDetailPage = f'{currentUrListItemDetail}page/' # detaylı url'e sayfa gezintisi için parametre eklendi.
        cListDom = fetch_page_dom(currentUrListItemDetail) # şu anki liste sayfasını oku.

        try: cListOwner = get_body_content(cListDom,'data-owner') # liste sahibini al.
        except Exception as e:
            print(f'{ICON_ERROR}Liste sahibi bilgisi alınamadı')
            txtLog(f'Liste sahibi bilgisi alınamadı Hata: {e}')
            cListOwner = 'Unknown'
        cListDomainName = extract_list_domain_name(currentUrListItem) # liste domain ismini düzenleyerek alır.
        cListRunTime = get_run_time() # liste işlem vaktini al. 

        listSignature({
            "list_detail_page": currentUrListItemDetailPage, # https://letterboxd.com/{un}/list/{ln}/detail/page/
            "list_detail_url": currentUrListItemDetail, # https://letterboxd.com/{un}/list/{ln}/detail/
            "list_domain_name": cListDomainName, # {ln}
            "process_state": processState, #  [1/1]
            "list_run_time": cListRunTime, # 14072023022401
            "list_url": currentUrListItem, # https://letterboxd.com/{un}/list/{ln}
            "list_owner": cListOwner, # {un}
            "list_dom": cListDom # <html>...</html>
        }) # liste hakkında bilgiler bastırılır.

        if listEnterPassOn:
            listEnter = input(f"{ICON_INPUT}Press enter to confirm the entered information. ({blink_text('Enter', 'green')})")

            if listEnter == "": listEnter, autoEnterMsg = True, '[Manual]'
            elif listEnter == ".":
                listEnter, autoEnterMsg = True, '[Auto]'
                listEnterPassOn = False
                print(f'{ICON_INFO}Listeler otomatik olarak onaylanacak şekilde ayarlandı.')
            else:
                listEnter = False
                print(f"{ICON_INFO}The {colored('session was canceled','red', attrs=['dark'])} because you did not verify the information.")
                txtLog(f'{PRE_LOG_INFO}The session was canceled because you did not verify the information.')

        if listEnter:
            txtLog(f'{PRE_LOG_INFO}Şimdiki listeye erişim başlatılıyor.')
            print(SUP_LINE)
            print(f"{ICON_INFO}{colored(f'List confirmed. {autoEnterMsg}', color='green')}")

            lastPageNo = get_list_last_page_no(cListDom, currentUrListItemDetailPage)
            openCsv = ''.join([exports_path, cListOwner, '_', cListDomainName, '_', cListRunTime, '.csv'])
            ensure_directories_exist([exports_path]) # export klasörünün kontrolü.
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
            print(f'{ICON_INFO}{loopCount-1} film {blink_text(openCsv,"yellow")} dosyasına aktarıldı.') # print info
            print(f"{ICON_INFO}{colored(f'{processState} completed!', 'green')}") # print info
            txtLog(f'{PRE_LOG_INFO}{processState} completed!') # log info
            print(SUB_LINE)

    combineCsv(url_list, export_directory_name, session_current_hash, exports_path) # merge csv files

    # session end
    endSession(session_current_hash)
    set_terminal_title(f'Session: {session_current_hash} ended!') # change title
    print(f"{ICON_INFO}{colored(f'Session: {session_current_hash} ended.', 'green')}") # print info
    txtLog(f'{PRE_LOG_INFO}Session: {session_current_hash} ended.') # log info

    # process end
    print(f"{ICON_INFO}Process State: {blink_text(processState +' Finish.','green')}")
    execute_terminal_command(f"echo {ICON_INFO}{blink_text('Press enter to continue with the new session.','yellow')} & pause >nul")