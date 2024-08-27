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


def export_films_to_csv(csv_path: str, last_page_no: int, detail_page_url: str) -> None:
    with open(csv_path, 'w', newline='', encoding="utf-8") as file: # konumda Export klasörü yoksa dosya oluşturmayacaktır.
        writer = csv.writer(file)
        header = ['Year', 'Title', 'LetterboxdURI']
        writer.writerow(header) # csv açıldıktan sonra en üste yazılacak başlıklar.

        count = 1
        print(SUP_LINE_FILMS, end='')
        for x in range(int(last_page_no)): # sayfa sayısı kadar döngü oluştur.
            txtLog(f'{PRE_LOG_INFO}Connecting to {detail_page_url}{str(x+1)}') # sayfa numarasını log dosyasına yaz.
            current_dom = fetch_page_dom(f'{detail_page_url}{str(x+1)}') # sayfa dom'u alınır.
            count = extract_and_write_films(count, current_dom, writer) # filmleri al.
        file.close() # açtığımız dosyayı manuel kapattık

    context = {
        'count': count
    }

    return context

def print_session_hash(session_start_hash: str, session_current_hash: str) -> None:
    """
    Compares the session start hash with the current session hash and prints the result.

    Args:
        session_start_hash (str): The initial hash of the session.
        session_current_hash (str): The current hash of the session.

    The function performs the following:
    1. Checks if the session start hash is the same as the current session hash.
    2. Highlights the differences between the hashes if they are not the same.
    3. Prints the session hash comparison, showing the changes if any.
    """
    is_same_hash = session_start_hash == session_current_hash
    hash_changes = highlight_changes(session_start_hash, session_current_hash)
    
    print(f"{ICON_INFO}Session Hash: {session_start_hash}{'' if is_same_hash else ' -> ' + hash_changes}")

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

    print_session_hash(session_start_hash, session_current_hash)

    # While initializing
    listEnterPassOn = True
    break_loop = False
    inputLoopNo = 0
    url_list = []
    while True:
        # Başlangıçta döngü değerini artırıyoruz.
        inputLoopNo += 1 
        # Kullanıcıdan liste url'i alınması ve düzenlenmesi.
        url_list_item = str(input(f'{ICON_INPUT}List URL[{inputLoopNo}]: ')).lower()
        if len(url_list_item) > 0: ## Giriş boş değilse..

            # Input starts with split parameter
            if url_list_item[0:len(SPLIT_PARAMETER)] == SPLIT_PARAMETER: 
                splitCsv(url_list_item[len(SPLIT_PARAMETER):], export_directory_name, session_current_hash)
                # Restore loop number
                inputLoopNo -= 1
                continue

            if url_list_item[-1] == '.' and url_list_item[0] != '?':
                if not inputLoopNo > 1:
                    print(f"{ICON_INFO}To finish, you must first specify a list.") 
                    inputLoopNo -= 1
                    continue

            if '.' in url_list_item:
                # Girişte nokta varsa..
                if url_list_item[-1] == '.' or url_list_item == '.':
                    # Giriş nokta ile bitiyor veya tek nokta ise..
                    # Url alımını sonlandıracak bilgi.
                    break_loop = True 

                    if not url_list_item[0] == '?':
                        print(f'{ICON_INFO}Parametre tanındı, liste alım işlemi sonlandırıldı.')

                    if url_list_item[0] == '?' or url_list_item == ".." or url_list_item[-2:] == "..": 
                        print(f'{ICON_INFO}Ek parametre tanındı, liste arama sonrası tüm listeler otomatik onaylanacak.')
                        # Otomatik onaylama yapacak bilgi.
                        listEnterPassOn, listEnter, autoEnterMsg = False , True, '[Auto]'

                    if len(url_list) > 0:
                        # URL listesi boş değilse
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
                                # Başarısız girişlerde döngü sayısının normale çevrilmesi.
                                inputLoopNo -= 1 
                                continue
                url_list_item = trim_end(url_list_item, '.')

            if url_list_item[0] == '?': 
                print(f'{ICON_INFO}Paremetre tanındı: Liste arama modu.')
                # Başlangıçdaki soru işaret kaldırıldı.
                url_list_item = url_list_item[1:]

                if "!" in url_list_item:
                    # Son liste belirleyicisi
                    x = -1
                    for i in range(3):
                        # Sona en fazla 3 rakam girilebilir. letterboxd'da max bulubilen liste sayısı 250
                        if url_list_item[x-1] == "!":
                            endList = int(url_list_item[x:])
                            url_list_item = url_list_item[:x-1]
                        x += -1
                else:
                    # Son liste için bir parametre belirtilmezse.
                    endList = 'Not specified.'

                searchList = f'{SITE_DOMAIN}/search/lists/{url_list_item}/'
                searchListPreviewDom = fetch_page_dom(searchList)
                searchMetaTitle = get_meta_content(searchListPreviewDom,'og:title')
                searchLMetaUrl = get_meta_content(searchListPreviewDom,'og:url')

                try:
                    #: Kaç liste bulunduğu hakkında bilgi veren mesaj.
                    searchListsQCountMsg = searchListPreviewDom.find('h2', attrs={'class':'section-heading'}).text
                except AttributeError:
                    print(f"{ICON_ERROR}Bir etiketten 'arama karşılama mesajı' alınamadı.")
                    txtLog(f"Bir etiketten 'arama karşılama mesajı' alınamadı. Hata Mesajı: {AttributeError}")
                    searchListsQCountMsg = ''

                try:
                    # Son sayfayı alıyoruz.
                    searchListsQLastsPage = searchListPreviewDom.find_all('li',attrs={'class':'paginate-page'})[-1].text
                except:
                    # Alınamazsa sayfada tek sayfa olduğu varsayılır.
                    searchListsQLastsPage = 1
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

                """ XXX """

                sayfa, liste = 0, 0
                for i in range(int(searchListsQLastsPage)):
                    sayfa += 1
                    connectionPage = f'{searchList}page/{sayfa}'
                    searchListDom = fetch_page_dom(connectionPage)
                    # Okunmuş sayfadaki tüm listelerin adresleri.
                    listsUrls = searchListDom.find_all('a', attrs={'class':'list-link'})

                    # Query page summary
                    print_colored_dict({
                        "Process": {
                            "Current Page": sayfa,
                            "Page URL": connectionPage,
                            "Lists Count": len(listsUrls)
                        }
                    })

                    """ Start: Processing and Validating URL Lists """
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
                    else:
                        continue
                    """ End: Processing and Validating URL Lists """
                    print(SUB_LINE)
                    break
                """ XXX """
                break
            # If url is detail page, remove detail part.
            url_list_item = remove_substring(url_list_item, '/detail') 
            # Sayfa dom'u alınır.
            urlListItemDom = fetch_page_dom(url_list_item)
            # Liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
            userListAvailable, approvedListUrl = check_user_list(urlListItemDom, url_list_item) 
            if userListAvailable:
                if approvedListUrl not in url_list:
                    # Doğrulanmış URL daha önce URL Listesine eklenmediyse..
                    # Doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
                    url_list.append(approvedListUrl)
                    if break_loop:
                        # Kullanıcı URL sonunda nokta belirttiyse.. URL alımını sonlandırıyoruz.
                        break
                else:
                    # Doğrulanmış URL daha önce işlem görecek URL listine eklenmiş ise..
                    # URL'in daha önce girildiğini ekrana yazdırıyoruz.
                    print(f'{ICON_ERROR}You have already entered this address list.')
                    # Başarısız girişlerde döngü sayısının normale çevrilmesi.
                    inputLoopNo -= 1 
            else:
                # Kullanıcının girdiği URL doğrulanmazsa..
                print(f"{ICON_INFO}You did not enter a valid url.")
                inputLoopNo -= 1
        else:
            # Kullanıcı genişliğe sahip bir değer girmez ise..
            print(f"{ICON_INFO}Just enter a period to move on to the next steps. You can also add it at the end of the URL.")
            inputLoopNo -= 1

    print(f"{ICON_INFO}List address acquisition terminated.")

    """ FOR INITIALIZING """

    process_loop_no = 0
    for current_url in url_list:
        process_loop_no += 1
        process_state = f'[{process_loop_no}/{len(url_list)}]'
        current_url_detail = f'{current_url}detail/' # url'e detail eklendi.
        current_url_detail_page = f'{current_url_detail}page/' # detaylı url'e sayfa gezintisi için parametre eklendi.
        current_dom_detail = fetch_page_dom(current_url_detail) # şu anki liste sayfasını oku.

        # Liste sahibi bilgisini ayıklıyoruz.
        try:
            current_list_owner = get_body_content(current_dom_detail, 'data-owner')
        except Exception as e:
            print(f'{ICON_ERROR}Liste sahibi bilgisi alınamadı')
            txtLog(f'Liste sahibi bilgisi alınamadı Hata: {e}')
            current_list_owner = 'Unknown'

        # Liste domain ismini düzenleyerek alır.
        # https://letterboxd.com/fastfingertips/list/list_name/ ~> list_name
        current_list_domain = extract_list_domain_name(current_url)
        # Liste işlem vaktini oluştur.
        current_list_runtime = get_run_time()

        # Liste hakkında bilgiler bastırılır.
        listSignature({
            "list_detail_page": current_url_detail_page, # https://letterboxd.com/{un}/list/{ln}/detail/page/
            "list_detail_url": current_url_detail, # https://letterboxd.com/{un}/list/{ln}/detail/
            "list_domain_name": current_list_domain, # {ln}
            "process_state": process_state, #  [1/1]
            "list_run_time": current_list_runtime, # 14072023022401
            "list_url": current_url, # https://letterboxd.com/{un}/list/{ln}
            "list_owner": current_list_owner, # {un}
            "list_dom": current_dom_detail # <html>...</html>
        })

        if listEnterPassOn:
            listEnter = input(f"{ICON_INPUT}Press enter to confirm the entered information. ({blink_text('Enter', 'green')})")

            if listEnter == "":
                listEnter, autoEnterMsg = True, '[Manual]'
            elif listEnter == ".":
                listEnter, autoEnterMsg = True, '[Auto]'
                listEnterPassOn = False
                print(f'{ICON_INFO}Listeler otomatik olarak onaylanacak şekilde ayarlandı.')
            else:
                listEnter = False
                print(f"{ICON_INFO}The {colored('session was canceled','red', attrs=['dark'])} because you did not verify the information.")
                txtLog(f'{PRE_LOG_INFO}The session was canceled because you did not verify the information.')

        if listEnter:
            print(SUP_LINE)
            print(f"{ICON_INFO}{colored(f'List confirmed. {autoEnterMsg}', color='green')}")

            last_page_no = get_list_last_page_no(current_dom_detail, current_url_detail_page)
            csv_path = ''.join([
                exports_path,
                current_list_owner, '_',
                current_list_domain, '_',
                current_list_runtime, '.csv'
            ])

            # Klasör ve dosya kontrolü.
            ensure_directories_exist([exports_path])
            ensure_files_exist([csv_path])

            loop_count = export_films_to_csv(csv_path, last_page_no, current_url_detail_page)

            """ PROCESS END """

            print(f'{ICON_INFO}{loop_count-1} film {blink_text(csv_path,"yellow")} dosyasına aktarıldı.')
            print(f"{ICON_INFO}{colored(f'{process_state} completed!', 'green')}")
            set_terminal_title(f'{process_state} completed!')
            txtLog(f'{PRE_LOG_INFO}{process_state} completed!')
            print(SUB_LINE)

    """ FOR END """
    
    # Merge csv files.
    combineCsv(url_list, export_directory_name, session_current_hash, exports_path)
    endSession(session_current_hash)
    set_terminal_title(f'Session: {session_current_hash} ended!')
    txtLog(f'{PRE_LOG_INFO}Session: {session_current_hash} ended.')
    print(f"{ICON_INFO}{colored(f'Session: {session_current_hash} ended.', 'green')}")
    print(f"{ICON_INFO}Process State: {blink_text(process_state +' Finish.','green')}")
    execute_terminal_command(f"echo {ICON_INFO}{blink_text('Press enter to continue with the new session.','yellow')} & pause >nul")