import sys
import csv
import requests
import arrow
import json
from datetime import datetime, timedelta, date, timezone
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from typing import Collection
from pandas import DataFrame
import os  # https://stackoverflow.com/a/48010814
# Term Color NET/lOCAL
try:
    from termcolor import colored, cprint
except:
    from labs.termcolor110.termcolor import colored, cprint

def settings_set():
    if os.path.exists('settings.json'):
        while True:
            try:
                with open("settings.json") as jsonFile:
                    jsonObject = json.load(jsonFile)
                    logDirName = jsonObject['log_dir']
                    exportDirName = jsonObject['export_dir']
                    break
            except Exception as msgExcept:
                print(f'Ayarlarınız {msgExcept} nedeniyle alınamadı.')
    else:
        while True:
            try:
                print('Ayar dosyası bulunamadı. Lütfen gerekli bilgileri girin.')
                logDirName = input('Log directory Name: ')
                exportDirName = input('Export directory Name: ')
                settings_dict = {
                    'log_dir': logDirName,
                    'export_dir': exportDirName,
                }
                with open('settings.json', 'w') as json_file:
                    json.dump(settings_dict, json_file)
                break
            except Exception as msgExcept:
                print(f'Ayarlarınız {msgExcept} nedeniyle kaydedilemedi.')
    return logDirName, exportDirName

def test_pause():
    os.system('echo Test için durduruluyor. & pause >nul')

def filtre_sor():
    # Filter req
    while True:
        filter_yn = input(
            f'{preCmdInput} Listeye filtre uygulanacak mı? [{colored("Y", color="green")}/{colored("N", color="red")}]: ').lower()
        if filter_yn == "y":
            w_filter = True
            logging(f'{preLogInfo}Listeye filtre uygulanacak.')
            bypassedFilters = 0
            while True:
                decadeyear_dory = input(f'\n{preCmdInput} Want {colored("D", color="green")}ecade or {colored("Y", color="green")}ear filter? [{colored("D", color="green")}/{colored("Y", color="green")}/{colored("N", color="red")}]: ').lower()
                if decadeyear_dory == "d":
                    # Çekmek yerine ürettik.
                    decade_year = 1870 #: min decade year
                    max_multiply = 16 #: 16*10 + 1870
                    decade_years = []
                    decade_nums = []
                    decade_num = 0
                    for i in range(max_multiply):
                        filterBlanks = ' ' if i < 10 else '' #: filterBlanks = ' ' if i in range(10) else ''
                        print(f'[{colored(decade_num, color="cyan")}] {filterBlanks}{decade_year}s')
                        decade_years.append(int(decade_year))
                        decade_year += 10
                        decade_nums.append(int(decade_num))
                        decade_num += 1
                    while True:
                        i_decadeyear = int(input(f'{preCmdInput} Decade [{colored("Num", color="cyan")}]: '))
                        if i_decadeyear >= min(decade_nums) and i_decadeyear <= max(decade_nums):
                            print(f'{preBlankCount}{colored("Selected:", color="green")} [{colored(i_decadeyear, color="cyan")}]: {decade_years[i_decadeyear]}s\n')
                            msgDecadeYear = f'  \u25E6 Decade:  [{i_decadeyear}]: {decade_years[i_decadeyear]}s\n'
                            w_decadeyear = f"/decade/{decade_years[i_decadeyear]}s"
                            decadeyear_confirm = True
                            break
                        else:
                            print(f'{preBlankCount}{colored("Belirtilen onyıllardan satır numarasını girmelisiniz.", color="red")}')
                elif decadeyear_dory == "y":
                    while True:
                        i_decadeyear = int(input(f'{preCmdInput} Year [{colored("1870", color="cyan")}-{colored("2029", color="blue")}]: '))
                        msgDecadeYear = f'Year: {i_decadeyear}\n'
                        w_decadeyear = f"/year/{i_decadeyear}"
                        decadeyear_confirm = True
                        # Linkler 1870 ve 2029'a kadar çalışıyor.
                        if i_decadeyear >= 1870 and i_decadeyear <= 2029:
                            print(f'{preBlankCount}{colored("Selected:", color="green")} {i_decadeyear}\n')
                            break
                        else:
                            print(f'{preBlankCount}{colored("Belirtilen aralıkta seçim yapınız.", color="red")}')
                elif decadeyear_dory == "n":
                    w_decadeyear = ''
                    msgDecadeYear = ''
                    print(f'{preBlankCount}Zaman aralığı filtresi uygulanmayacak.\n')
                    bypassedFilters = 1
                    decadeyear_confirm = True
                else:
                    print(f'{preBlankCount}{colored("Anlaşılmadı, tekrar deneyin.", color="red")}')
                    decadeyear_confirm = False
                # decade ve year işlemleri tamamsa çıkalım
                if decadeyear_confirm:
                    break
            while True:
                genre_dory = input(f'{preCmdInput} Want genre filter? [{colored("Y", color="green")}/{colored("N", color="red")}]:').lower()
                if genre_dory == "y":
                    genre_filter_name, genre_filter_adress, filterNum = getUlFilters(3) #: Buradaki 3 bizim 4. Ul'a gitmemize yarayacak.
                    strip_genre = genre_filter_adress.replace(f'/{userName}/list/{list_name}detail', "") # Gelen filtre adresini düzenliyoruz. Son kısmını alıyoruz
                    msgGenre = f'  \u25E6 Genre:   [{filterNum}]: {genre_filter_name}\n'
                    w_genre = strip_genre
                    genre_confirm = True
                elif genre_dory == "n":
                    w_genre = ''
                    msgGenre = ''
                    print(f'{preBlankCount}Genre filtresi uygulanmayacak.\n')
                    bypassedFilters += 1
                    genre_confirm = True
                else:
                    print("Anlaşılmadı. Tekrar deneyin.", end='')
                    genre_confirm = False
                if genre_confirm:
                    break
            while True:
                sortby_dory = input(f'{preCmdInput} Want Sort By filter? [{colored("Y", color="green")}/{colored("N", color="red")}]: ').lower()
                if sortby_dory == "y":
                    sortby_filter_name, sortby_filter_adress, filterNum = getUlFilters(1) #: Buradaki 1 bizim 2. Ul'a gitmemize yarayacak.
                    # Gelen filtre adresini düzenliyoruz. Son kısmını alıyoruz
                    strip_sortby = sortby_filter_adress.replace(f'/{userName}/list/{list_name}detail', "")
                    msgSortby = f'  \u25E6 Sort By: [{filterNum}]: {sortby_filter_name}\n'
                    w_sortby = strip_sortby
                    sortby_confirm = True
                elif sortby_dory == "n":
                    w_sortby = ''
                    msgSortby = ''
                    print('  Sort By filtresi uygulanmayacak.\n')
                    bypassedFilters += 1
                    sortby_confirm = True
                else:
                    sortby_confirm = False
                    print("  Anlaşılmadı. Tekrar deneyin.")
                if sortby_confirm:
                    break
            filterConfirm = True #: Filtre elemanları bittikten sonra while için filtre onayı
        elif filter_yn == "n": #: Filtre istemezse
            w_filter = False
            w_decadeyear, w_genre, w_sortby = '', '', ''
            msgDecadeYear, msgGenre, msgSortby = '', '', ''
            bypassedFilters = 3
            filterConfirm = True
            logging(f'{preLogInfo}Listeye filtre uygulanmayacak.')
        else: #: Filtre isteyip istemediği anlaşılmayınca
            filterConfirm = False
            print("Tam anlayamadık? Tekrar deneyin.")
            logging(f'{preLogInfo}Kullanıcı soruya cevap veremedi.')
        if filterConfirm: #: While döngüsünden çıkmak için.
            break
    allFiltres = f'{w_decadeyear}{w_genre}{w_sortby}'
    filtresMsg = f'{msgDecadeYear}{msgGenre}{msgSortby}'
    return allFiltres, w_filter, filtresMsg, bypassedFilters

def getUlFilters(tempUlNum): #: Sıralama yöntemlerini çekmek. Genre: 3, Sortby: 1
    # Filtre yöntemlerinden listenin sıralama yöntemleri olan ul etiketini yani 2.sıradaki ul'u seçtik.
    filtersDom = soup.find_all('ul', attrs={'class': 'smenu-menu'})[tempUlNum].find_all("li") # şu anki dom içinde belirtilen ul içindeki filtreler.
    currentFilterNumber = 0
    filterNames, filterAdresses = [], [] #: İsimler ve filtreler için boş küme oluşturduk.
    for currentFilter in filtersDom:
        
        try: #: Seçimin başlığı var mı?
            filter_sub = currentFilter.find('span').text
            print(f'{filter_sub}')
            currentFilterNumber -= 1
        except: #: Seçimin başlığı yoksa
            try:
                filterBlanks = ' ' if currentFilterNumber < 10 else '' #: İlk 10 Liste elemanı için boşluk ayarlar,
                print(f'[{colored(currentFilterNumber, color="cyan")}]: {filterBlanks}', end=' ') #: ve hizalarız.
                try: #: Liste ismini almayı deneriz.
                    currentFilterName = currentFilter.find('a').text
                except:
                    currentFilterName = currentFilter.text
                finally:
                    filterNames.append(str(currentFilterName))
                    print(currentFilterName)
                    print("test")
                try: #: Liste elemanının adresini almayı deneriz.
                    currentFilterAdress = currentFilter.find('a')['href']
                except:
                    currentFilterAdress = currentFilter.find('href')
                finally:
                    filterAdresses.append(str(currentFilterAdress))
            except:
                pass
        currentFilterNumber += 1
    # Kullanıcı bir eleman seçer
    filterNum = int(input(f'{preCmdInput} Filter [{colored("Num", "cyan")}]: '))
    print(f'{preBlankCount}{colored("Selected:", color="green")} [{colored(filterNum, color="cyan")}]: {filterNames[filterNum]}\n')
    return filterNames[filterNum], filterAdresses[filterNum], filterNum

def signature(x): #: x: 0 ilk, 1 son
    try:
        if x == True:
            os.system('cls') #: İlk imza gösteriminde öncesini temizle.
            print(colored('Your Inputs;', color="yellow"))
            if w_filter and bypassedFilters < 3:
                print(f'{preCmdMiddleDot} User: {userName}\n{preCmdMiddleDot} List: {list_name}\n{preCmdMiddleDot} Filtre uygulaması: Var\n{filtresMsg}')
            else:
                print(f'{preCmdMiddleDot} User: {userName}\n{preCmdMiddleDot} List: {list_name}\n{preCmdMiddleDot} Filtre uygulaması: Yok\n')
            try: #: Liste sayfasından bilgiler çekmek.
                print(colored('List info;', color="yellow"))
                listBy = soup.select("[itemprop=name]")[0].text #: Liste sahibin ismini çektik
                print(f'{preCmdMiddleDot} List by {listBy} (@{userName})')
                listTitle = soup.select("[itemprop=title]")[0].text.strip() #: Liste başlığının ismini çektik
                print(f'{preCmdMiddleDot} List title: {listTitle}')
                print(f'{preCmdMiddleDot} Number of movies: {getMovieCount(getListLastPageNo())}') # Film sayısını yazdırdık
                listPublicationTime = soup.select(".published time")[0].text #: Liste oluşturulma tarihi
                listPtime = arrow.get(listPublicationTime)#: arrow: https://arrow.readthedocs.io/en/latest/
                print(f'{preCmdMiddleDot} Published: {listPtime.humanize()}') #: or print(f'Published: {listPtime.humanize(granularity=["year","month", "day", "hour", "minute"])}')
                #!< now_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") #: utcnow: https://newbedev.com/python-utc-datetime-object-s-iso-format-doesn-t-include-z-zulu-or-zero-offset
                # s = arrow.get(now_time) | time_x = s-f | print(f'Time since publication: {time_x}')
                try: #: Search list update time
                    search_listUtime = soup.select(".updated time")[0].text
                    listUtime = arrow.get(search_listUtime)
                    msg_Utime = listUtime.humanize()
                except:
                    msg_Utime = 'No editing'
                finally:
                    print(f'{preCmdMiddleDot} Updated: {msg_Utime}')
            except:
                logging(f'{preLogErr}Film sahibi görünür adı ve liste adı istenirken hata oluştu.')
        else:
            print(f'\n{preCmdMiddleDot} Filename: {csvFileName}\n{preCmdMiddleDot} Film sayısı: {loopCount-1}\n{preCmdMiddleDot} Tüm filmler ', end="")
            cprint(open_csv, 'yellow', attrs=['blink'], end=" dosyasına aktarıldı.\n")
            try: #: Seçili olan filtreyi yazdırdık.
                search_selected_decadeyear = currentDom.select(".smenu-subselected")[3].text
                print(f'{preCmdMiddleDot} Filtered as {search_selected_decadeyear} movies only was done by')
                search_selected_genre = currentDom.select(".smenu-subselected")[2].text
                print(f'{preCmdMiddleDot} Filtered as {search_selected_genre} only movies')
                search_selected_sortby = currentDom.select(".smenu-subselected")[0].text
                print(f'{preCmdMiddleDot} Movies sorted by {search_selected_sortby}')
            except:
                logging(f'{preLogErr}Film filtre bilgileri alınamadı..')
        log = f'{preLogInfo}İmza yazdırma işlemleri tamamlandı.'
    except:
        print('İmza seçimi başarısız.')
        log = f'{preLogErr}İmza yüklenemedi. Program yine de devam etmeyi deneyecek.'
    finally:
        logging(log)

def dir_check(l, e): # l= LOG FILE, e = EXPORT FILE
    # Buradaki ifler tekli kontrol yapabş-ilmemize yarar. Örneğin e'yi false yollarım ve sadece l'yi çekebilirim.
    if l: #: Log directory
        if os.path.exists(l):
            logging(f'{preLogInfo}{l} klasörü halihazırda var.')
        else:
            os.makedirs(l)
            logging(f'{preLogInfo}{l} klasörü oluşturuldu') #: Oluşturulamaz ise bir izin hatası olabilir.
    if e: #: Exports directory
        if os.path.exists(e):
            logging(f'{preLogInfo}{e} klasörü halihazırda var.')
        else:
            os.makedirs(e)
            logging(f'{preLogInfo}{e} klasörü oluşturuldu') #: Oluşturulamaz ise bir izin hatası olabilir.



def logging(r_message, r_loglocation=None): #: None: Kullanıcı log lokasyonunu belirtmese de olur.
    try:
        f = open(logFilePath, "a")
        f.writelines(f'{r_message}\n')
        f.close()
    except Exception as e:
        if r_loglocation is not None:
            print(f'Loglama işlemi {r_loglocation} konumunda {e} nedeniyle başarısız.')
        else:
            print(f'Loglama işlemi {e} nedeniyle başarısız.')

def readpage(tempUrl):
    try:
        urlResponseCode = requests.get(tempUrl)
        print(urlResponseCode)
        # > Sayfa kodları çekildi.
        urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')
        logging(f'{preLogInfo}Trying connect to [{tempUrl}]')
        return urlDom
    except:
        print('Connection to address failed.')
        logging(f'{preLogErr}Connection to address failed [{tempUrl}]')

def doPullFilms(tempLoopCount,tempCurrentDom): #: Filmleri çekiyoruz yazıyoruz
    try:
        # > Çekilen sayfa kodları, bir filtre uygulanarak daraltıldı.
        articles = tempCurrentDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
        loopCount = tempLoopCount
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
            print(f'{loopCount})  {movieName} ({movieYear})')
            writer.writerow([str(movieName), str(movieYear)])
            loopCount += 1
        return loopCount
    except:
        print('Film bilgilerini elde ederken bir hatayla karşılaşıldı.')

def check_user(): #: Kullanıcının var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        userDisplayName = profileVisit.select(".title-1")[0].text
        print(f'{preBlankCount}{colored("Found it: ", color="green")}{userDisplayName}')
        logging(f'{preLogInfo}{userName} kullanıcısı bulundu: {str(userDisplayName)}', check_user.__name__)
        userAvailable = True
    except:
        print(f'{preBlankCount}{colored("Kullanıcı bulunamadı. Tekrar deneyin.", color="red")}')
        logging(f'{preLogInfo}{userName} kullanıcısı bulunamadı.', check_user.__name__)
        userAvailable = False
    finally:
        return userAvailable


def userListCheck(): #: Kullanıcının girilen şekilde bir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        # > bu meta etiketinden veri almayı deniyor eğer yoksa liste değil.
        try:
            meta_test = visitList.find('meta', property="og:type").attrs['content']
            # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşışılır
            if meta_test == "letterboxd:list":
                logging(f'{preLogInfo}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {meta_test}')
                # Liste ismini alıyoruz.
                currentListName = visitList.find('meta', property="og:title").attrs['content']
                print(f'{preBlankCount}{colored("Found it: ", color="green")}{currentListName}')
                # Liste yönlendirimesi var mı bakıyoruz
                currentUrl = visitList.find('meta', property="og:url").attrs['content']
                if currentUrl == visitUserListUrl:
                    logging(f'{preLogInfo}Liste adresi yönlendime içermiyor.')
                    currentUrl = visitUserListUrl
                else:
                    print(f'[{colored("!", color="yellow")}] Girdiğiniz liste linki eskimiştir, muhtemelen liste ismi yakın bir zamanda değişildi.')
                    print(f'{preBlankCount}{colored(visitUserListUrl, color="yellow")} adresini değiştirdik.')
                    print(f'{preBlankCount}{colored(currentUrl, color="green")} adresinden devam ediyoruz.')
                logging(f'{preLogInfo}{list_name} listesi bulundu: {currentListName}')
                currentListAvaliable = True
        except:
            print(f'{preBlankCount}Bu kullanıcının böyle bir listesi yok.')
            currentUrl = ''
            currentListAvaliable = False
    except:
        currentListAvaliable = False
    finally:
        return currentListAvaliable, currentUrl

def getListLastPageNo():  # Listenin son sayfasını öğren
    try:
        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
        logging(f'{preLogInfo}Listedeki sayfa sayısı denetleniyor..')
        lastPageNo = soup.find('div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text
        logging(f'{preLogInfo}Liste birden çok sayfaya ({lastPageNo}) sahiptir.')
        getMovieCount(lastPageNo)
    except:
        # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        lastPageNo = 1
        getMovieCount(lastPageNo)
        logging(f'{preLogInfo}Birden fazla sayfa yok, bu liste tek sayfadır.')
    finally:
        logging(f'{preLogInfo}Sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPageNo} olduğu öğrenildi.')
        return lastPageNo

def getMovieCount(tempLastPageNo):  # Film sayısını öğreniyoruz
    try:
        # > Son sayfaya bağlanmak için bir ön hazırlık.
        lastPageDom = readpage(f'{url}{tempLastPageNo}')
        # > Sayfa kodları çekildi.
        lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
        lastPageMoviesCount =  len(lastPageArticles) #: Number of movies.
        # < Film sayısı öğrenildi.
        # > Toplam film sayısını belirlemek.
        movieCount = ((int(tempLastPageNo)-1)*100)+lastPageMoviesCount
        logging(f"{preLogInfo}Listedeki film sayısı {movieCount} olarak bulunmuştur.")
        return movieCount
    except:
        print(f'Film sayısını elde ederken hata.')
        logging(f'{preLogErr}Film sayısı elde edilirkren hata oluştu.s')

def doReset():  # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except:
        log = 'Programın yeniden başlatılmaya çalışılması başarısız.'
        print(log)
        logging(preLogErr + log)

def cmdPre(s,c):
    return f'[{colored(s, color=c)}]'
# > cprint ASCII Okuyabilmesi için program başlarken bir kere color kullanıyoruz: https://stackoverflow.com/a/61684844
# > Sonrasında hem temiz bir başlangıç hem de yeniden başlatmalarda Press any key.. mesajını kaldırmak için cls.
os.system('color & cls')

# > Saf domain'in parçalanarak birleştirilmesi
siteProtocol, siteUrl = "https://", "letterboxd.com/"
siteDomain = siteProtocol + siteUrl

## Mesajlar, Log Mesaj atamaları
# Cmd
preCmdInput = cmdPre(">","green")
preCmdErr = cmdPre("!","red")
preCmdMiddleDot = cmdPre(u"\u00B7","cyan") # middle dot
preBlankCount = 4*' '
# Log
preLogInfo = "Bilgi: "
preLogErr = "Hata: "
# Messages
msgCancel = "Bilgileri doğrulamadığınız için oturum iptal edildi."
# Run time check - Generate session hash
cmdRunTime = datetime.now().strftime('%d%m%Y%H%M%S')
print(f'[{colored("#", color="yellow")}] Session hash: ', end="") # Oturum için farklı bir isim üretildi.
cprint(cmdRunTime, 'yellow', attrs=['blink'])
logDirName, exportDirName = settings_set()
# Log file path
logFilePath = f'{logDirName}/{cmdRunTime}.txt'
dir_check(logDirName, False) # Log file check
print(f'[{colored("#", color="yellow")}] Log location created: ', end="")
cprint(logFilePath, 'yellow', attrs=['blink'])

while True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    userName = str(input(f'{preCmdInput} Username(Not display name): ')).lower()
    # Kullanıcı mevcutmu bakıyoruz
    profileVisit = readpage(f'{siteDomain}{userName}')
    userAvailable = check_user()
    if userAvailable:
        break

csvFileName = f"{userName}-({cmdRunTime})" #: Dosya çakışma sorunları için farklı isimler ürettik.
try: #: İşlem yapılan kişinin ismine göre log dosyasının isminin değiştirilmesi.
    approved_session = f'{logDirName}/{csvFileName}.txt'
    os.rename(logFilePath, approved_session) #: Os rename ile dizin belirterek dosya taşınabilir
    logFilePath = approved_session
    print(f'[{colored("#", color="yellow")}] Username added to log file: ', end="")
    cprint(logFilePath, 'yellow', attrs=['blink'])
except Exception as msgExcept:
    print(f"Log dosyasının ismi {msgExcept} nedeniyle değiştirilemedi.")
open_csv = f'{exportDirName}/{csvFileName}.csv'

while True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    list_name = str(input(f'{preCmdInput} Listname(Domain): ')).lower()
    # Kullanıcının böyle bir listesi mevcutmu bakıyoruz
    visitUserListUrl = f'{siteDomain}{userName}/list/{list_name}/'
    visitList = readpage(visitUserListUrl)
    userListAvailable, approvedListUrl = userListCheck()
    # Listenin asıl ismi
    # Approverd boş geldiğinde boşluk değerini değiştirmez
    list_name = approvedListUrl.replace(f'{siteDomain}{userName}/list/', "")
    if userListAvailable:
        break

editedListVisitUrl = f'{approvedListUrl}detail/' # Guest generate url. approvedListUrl https://letterboxd.com/username/list/listname/
soup = readpage(editedListVisitUrl)
# Filtrelerin çekilmesi ve domaine uygulanması
allFiltres, w_filter, filtresMsg, bypassedFilters = filtre_sor()
# Filtreler varsa URL'e işleniyor
url = f'{editedListVisitUrl}{allFiltres}page/'
print(f'url: {url}')
# Karşılama mesajı, kullanıcının girdiği bilgleri ve girilen bilgilere dayanarak listenin bilgilerini yazdırır.
signature(1)
# > Domain'in doğru olup olmadığı kullanıcıya sorulur, doğruysa kullanıcı enter'a basar ve program verileri çeker.
print(f'{preCmdMiddleDot} Link: {editedListVisitUrl}{allFiltres}')
ent = input(f'\n{preCmdInput} Press enter to confirm the entered information. (Enter)')
if ent == "":
    print(f'{preBlankCount}{colored("Liste bilgilerini onayladınız.", color="green")}')
    logging(f'{preLogInfo}Saf sayfaya erişim başlatılıyor.')
    soup = readpage(editedListVisitUrl+allFiltres) #: Verinin çekileceği dom'a filtre ekleniyor.
    lastPageNo = getListLastPageNo()
    print(type(lastPageNo))
    dir_check(False, exportDirName) #: Export klasörünün kontrolü.
    with open(f'{open_csv}', 'w', newline='', encoding="utf-8") as file: #: Konumda Export klasörü yoksa dosya oluşturmayacaktır.
        writer = csv.writer(file)
        writer.writerow(["Title", "Year"])
        # Filmleri çekiyoruz
        loopCount = 1
        # x sıfırdan başlıyor
        print("\nListedeki filmler:")
        for x in range(int(lastPageNo)):
            logging(f'Connecting to: {url}{str(x+1)}')
            currentDom = readpage(f'{url}{str(x+1)}')
            loopCount = doPullFilms(loopCount, currentDom)
        # Açtığımız dosyayı manuel kapattık
        file.close()
    logging(f'{preLogInfo}Success!')
    signature(0)
    doReset()
else:
    print(msgCancel)
    logging(preLogInfo + msgCancel)
    doReset()