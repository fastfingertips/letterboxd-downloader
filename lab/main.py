import os #: https://stackoverflow.com/a/48010814
import sys
import csv
import json
import arrow
import requests
from pandas import DataFrame
from bs4 import BeautifulSoup
from typing import Collection
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date, timezone
try: #: Term Color NET/lOCAL
    from termcolor import colored, cprint
except:
    from libs.termcolor110.termcolor import colored, cprint

def dirCheck(l, e): # l= LOG FILE, e = EXPORT FILE
    # Buradaki ifler tekli kontrol yapabş-ilmemize yarar. Örneğin e'yi false yollarım ve sadece l'yi çekebilirim.
    if l: #: Log directory
        if os.path.exists(l):
            txtLog(f'{preLogInfo}{l} klasörü halihazırda var.')
        else:
            os.makedirs(l)
            txtLog(f'{preLogInfo}{l} klasörü oluşturuldu') #: Oluşturulamaz ise bir izin hatası olabilir.
    if e: #: Exports directory
        if os.path.exists(e):
            txtLog(f'{preLogInfo}{e} klasörü halihazırda var.')
        else:
            os.makedirs(e)
            txtLog(f'{preLogInfo}{e} klasörü oluşturuldu') #: Oluşturulamaz ise bir izin hatası olabilir.
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
def doReadPage(tempUrl): #: Url'si belirtilen saufanın okunup, dom alınması.
    try:
        urlResponseCode = requests.get(tempUrl)
        # > Sayfa kodları çekildi.
        urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')
        txtLog(f'{preLogInfo}Trying connect to [{tempUrl}]')
        return urlDom
    except:
        print('Connection to address failed.')
        txtLog(f'{preLogErr}Connection to address failed [{tempUrl}]')
def doReset():  # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except:
        log = 'Programın yeniden başlatılmaya çalışılması başarısız.'
        print(log)
        txtLog(preLogErr + log)

def getListLastPageNo():  # Listenin son sayfasını öğren
    try:
        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
        txtLog(f'{preLogInfo}Listedeki sayfa sayısı denetleniyor..')
        lastPageNo = soup.find('div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text
        txtLog(f'{preLogInfo}Liste birden çok sayfaya ({lastPageNo}) sahiptir.')
        getMovieCount(lastPageNo)
    except:
        # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        lastPageNo = 1
        getMovieCount(lastPageNo)
        txtLog(f'{preLogInfo}Birden fazla sayfa yok, bu liste tek sayfadır.')
    finally:
        txtLog(f'{preLogInfo}Sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPageNo} olduğu öğrenildi.')
        return lastPageNo
def getMovieCount(tempLastPageNo):  # Film sayısını öğreniyoruz
    try:
        # > Son sayfaya bağlanmak için bir ön hazırlık.
        lastPageDom = doReadPage(f'{url}{tempLastPageNo}')
        # > Sayfa kodları çekildi.
        lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
        lastPageMoviesCount =  len(lastPageArticles) #: Number of movies.
        # < Film sayısı öğrenildi.
        # > Toplam film sayısını belirlemek.
        movieCount = ((int(tempLastPageNo)-1)*100)+lastPageMoviesCount
        txtLog(f"{preLogInfo}Listedeki film sayısı {movieCount} olarak bulunmuştur.")
        return movieCount
    except:
        print(f'Film sayısını elde ederken hata.')
        txtLog(f'{preLogErr}Film sayısı elde edilirkren hata oluştu.s')
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
def settingsFileSet(): #: Ayar dosyası kurulumu.
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
def signature(x): #: x: 0 ilk, 1 son
    try:
        if x == True:
            os.system('cls') #: İlk imza gösteriminde öncesini temizle.
            try: #: Liste sayfasından bilgiler çekmek.
                print(colored('List info;', color="yellow"))
                listBy = soup.select("[itemprop=name]")[0].text #: Liste sahibin ismini çektik
                print(f'{preCmdMiddleDot} List by {listBy}')
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
                txtLog(f'{preLogErr}Film sahibi görünür adı ve liste adı istenirken hata oluştu.')
        else:
            print(f'\n{preCmdMiddleDot} Filename: {open_csv}\n{preCmdMiddleDot} Film sayısı: {loopCount-1}\n{preCmdMiddleDot} Tüm filmler ', end="")
            cprint(open_csv, 'yellow', attrs=['blink'], end=" dosyasına aktarıldı.\n")
            try: #: Seçili olan filtreyi yazdırdık.
                search_selected_decadeyear = currentDom.select(".smenu-subselected")[3].text
                print(f'{preCmdMiddleDot} Filtered as {search_selected_decadeyear} movies only was done by')
                search_selected_genre = currentDom.select(".smenu-subselected")[2].text
                print(f'{preCmdMiddleDot} Filtered as {search_selected_genre} only movies')
                search_selected_sortby = currentDom.select(".smenu-subselected")[0].text
                print(f'{preCmdMiddleDot} Movies sorted by {search_selected_sortby}')
            except:
                txtLog(f'{preLogErr}Film filtre bilgileri alınamadı..')
        log = f'{preLogInfo}İmza yazdırma işlemleri tamamlandı.'
    except:
        print('İmza seçimi başarısız.')
        log = f'{preLogErr}İmza yüklenemedi. Program yine de devam etmeyi deneyecek.'
    finally:
        txtLog(log)
def txtLog(r_message, r_loglocation=None): #: None: Kullanıcı log lokasyonunu belirtmese de olur.
    try:
        f = open(logFilePath, "a")
        f.writelines(f'{r_message}\n')
        f.close()
    except Exception as e:
        if r_loglocation is not None:
            print(f'Loglama işlemi {r_loglocation} konumunda {e} nedeniyle başarısız.')
        else:
            print(f'Loglama işlemi {e} nedeniyle başarısız.')
def userListCheck(): #: Kullanıcının girilen şekilde bir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        # > bu meta etiketinden veri almayı deniyor eğer yoksa liste değil.
        try:
            meta_test = visitList.find('meta', property="og:type").attrs['content']
            # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşışılır
            if meta_test == "letterboxd:list":
                txtLog(f'{preLogInfo}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {meta_test}')
                # Liste ismini alıyoruz.
                currentListName = visitList.find('meta', property="og:title").attrs['content']
                print(f'{preBlankCount}{colored("Found it: ", color="green")}{currentListName}')
                # Liste yönlendirimesi var mı bakıyoruz
                currentUrl = visitList.find('meta', property="og:url").attrs['content']
                if currentUrl == visitUserListUrl:
                    txtLog(f'{preLogInfo}Liste adresi yönlendime içermiyor.')
                    currentUrl = visitUserListUrl
                else:
                    print(f'[{colored("!", color="yellow")}] Girdiğiniz liste linki eskimiştir, muhtemelen liste ismi yakın bir zamanda değişildi.')
                    print(f'{preBlankCount}{colored(visitUserListUrl, color="yellow")} adresini değiştirdik.')
                    print(f'{preBlankCount}{colored(currentUrl, color="green")} adresinden devam ediyoruz.')
                txtLog(f'{preLogInfo}{listUrl} listesi bulundu: {currentListName}')
                currentListAvaliable = True
        except:
            print(f'{preBlankCount}Bu kullanıcının böyle bir listesi yok.')
            currentUrl = ''
            currentListAvaliable = False
    except:
        currentListAvaliable = False
    finally:
        return currentListAvaliable, currentUrl
def test_pause(): #: Geliştirici duraklatmaları için kalıp.
    os.system('echo Test için durduruluyor. & pause >nul')
def cmdPre(s,c): #: Mesaj ön ekleri için kalıp.
    return f'[{colored(s, color=c)}]'

# > cprint ASCII Okuyabilmesi için program başlarken bir kere color kullanıyoruz: https://stackoverflow.com/a/61684844
# > Sonrasında hem temiz bir başlangıç hem de yeniden başlatmalarda Press any key.. mesajını kaldırmak için cls.
os.system('color & cls')

## Saf domain'in parçalanarak birleştirilmesi
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
logDirName, exportDirName = settingsFileSet()
# Log file path
logFilePath = f'{logDirName}/{cmdRunTime}.txt'
dirCheck(logDirName, False) # Log file check
print(f'[{colored("#", color="yellow")}] Log location created: ', end="")
cprint(logFilePath, 'yellow', attrs=['blink'])

open_csv = f'{exportDirName}/{cmdRunTime}.csv' 

while True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    listUrl = str(input(f'{preCmdInput} List Url: ')).lower()
    # Kullanıcının böyle bir listesi mevcutmu bakıyoruz
    visitUserListUrl = listUrl
    visitList = doReadPage(visitUserListUrl)
    userListAvailable, approvedListUrl = userListCheck()
    # Listenin asıl ismi
    if userListAvailable:
        break

editedListVisitUrl = f'{approvedListUrl}detail/' # Guest generate url. approvedListUrl https://letterboxd.com/username/list/listname/
soup = doReadPage(editedListVisitUrl)
# Filtrelerin çekilmesi ve domaine uygulanması
# Filtreler varsa URL'e işleniyor
url = f'{editedListVisitUrl}page/'
print(f'url: {url}')
# Karşılama mesajı, kullanıcının girdiği bilgleri ve girilen bilgilere dayanarak listenin bilgilerini yazdırır.
signature(1)
# > Domain'in doğru olup olmadığı kullanıcıya sorulur, doğruysa kullanıcı enter'a basar ve program verileri çeker.
print(f'{preCmdMiddleDot} Link: {editedListVisitUrl}')
ent = input(f'\n{preCmdInput} Press enter to confirm the entered information. (Enter)')
if ent == "":
    print(f'{preBlankCount}{colored("Liste bilgilerini onayladınız.", color="green")}')
    txtLog(f'{preLogInfo}Saf sayfaya erişim başlatılıyor.')
    soup = doReadPage(editedListVisitUrl) #: Verinin çekileceği dom'a filtre ekleniyor.
    lastPageNo = getListLastPageNo()
    dirCheck(False, exportDirName) #: Export klasörünün kontrolü.
    with open(f'{open_csv}', 'w', newline='', encoding="utf-8") as file: #: Konumda Export klasörü yoksa dosya oluşturmayacaktır.
        writer = csv.writer(file)
        writer.writerow(["Title", "Year"])
        # Filmleri çekiyoruz
        loopCount = 1
        # x sıfırdan başlıyor
        print("\nListedeki filmler:")
        for x in range(int(lastPageNo)):
            txtLog(f'Connecting to: {url}{str(x+1)}')
            currentDom = doReadPage(f'{url}{str(x+1)}')
            loopCount = doPullFilms(loopCount, currentDom)
        # Açtığımız dosyayı manuel kapattık
        file.close()
    txtLog(f'{preLogInfo}Success!')
    signature(0)
    doReset()
else:
    print(msgCancel)
    txtLog(preLogInfo + msgCancel)
    doReset()