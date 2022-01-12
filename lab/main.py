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

def dirCheck(dirs): # l= LOG FILE, e = EXPORT FILE
    # Buradaki ifler tekli kontrol yapabş-ilmemize yarar. Örneğin e'yi false yollarım ve sadece l'yi çekebilirim.
    for dir in dirs:
        if dir: #: Log directory
            if os.path.exists(dir):
                txtLog(f'{preLogInfo}{dir} folder already exists.')
            else:
                os.makedirs(dir)
                txtLog(f'{preLogInfo}{dir} folder created.') #: Oluşturulamaz ise bir izin hatası olabilir.
    print(f'{preCmdInfo} Log location created: {cmdBlink(logFilePath, "yellow")}')


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
            print(f'{loopCount}) {movieName} ({movieYear})')
            writer.writerow([str(movieName), str(movieYear)])
            loopCount += 1
        return loopCount
    except:
        print('An error was encountered while obtaining movie information.')

def doReadPage(tempUrl): #: Url'si belirtilen saufanın okunup, dom alınması.
    try:
        urlResponseCode = requests.get(tempUrl)
        # > Sayfa kodları çekildi.
        urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')
        txtLog(f'{preLogInfo}Trying connect to [{tempUrl}]')
        return urlDom
    except:
        print(f'{preBlankCount}Connection to address failed.')
        txtLog(f'{preLogErr}Connection to address failed [{tempUrl}]')
def doReset():  # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except:
        log = 'Attempting to restart the program failed.'
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
        print(f'Error getting movie count.')
        txtLog(f'{preLogErr}Film sayısı elde edilirkren hata oluştu.')

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
        if x == True:                                                           ## İmza seçimi bu olması durumunda.
            try:                                                                ## Liste sayfasından bilgiler çekmek.
                print(colored('\nList info;', color="yellow"))                  #: Liste başlığı.
                                                                                ## Liste bilgileri alınır.
                listBy = soup.select("[itemprop=name]")[0].text                 #: Liste sahibin ismini çekiliyor.
                listTitle = soup.select("[itemprop=title]")[0].text.strip()     #: Liste başlığının ismini çekiliyor.
                listPublicationTime = soup.select(".published time")[0].text    #: Liste oluşturulma tarihi çekiliyor.
                listPT = arrow.get(listPublicationTime)                         #: Liste oluşturulma tarihi düzenleniyor. Arrow: https://arrow.readthedocs.io/en/latest/
                listMovieCount =  getMovieCount(getListLastPageNo())            #: Listedeki film sayısı hesaplanıyor.
                                                                                ## Liste bilgileri yazdırılır.
                print(f'{preCmdMiddleDot} List by {listBy}')                    # Liste sahibinin görünen adı yazdırılıyor.
                print(f'{preCmdMiddleDot} List title: {listTitle}')             #: Liste başlığı yazdırılıyor.
                print(f'{preCmdMiddleDot} Number of movies: {listMovieCount}')  #: Listede bulunan film sayısı yazdırılıyor.
                print(f'{preCmdMiddleDot} Published: {listPT.humanize()}')      #: or print(f'Published: {listPtime.humanize(granularity=["year","month", "day", "hour", "minute"])}')
                try:                                                            ## Search list update time
                    listUpdateTime = soup.select(".updated time")[0].text       #: Liste düzenlenme vakti çekiliyor.
                    listUT = arrow.get(listUpdateTime)                          #: Çekilen liste düzenlenme vakti düzenleniyor.
                    msgListUpdateTime = listUT.humanize()                       #: Çekilen liste düzenlenme vakti kullanıma hazırlanıyor.
                except:                                                         ## Hata alınırsa liste düzenlenmemiş varsayılır.
                    msgListUpdateTime = 'No editing.'                           #: Liste düzenlenmemiş.
                finally:                                                        ## Kontrol sonu işlemleri.
                    print(f'{preCmdMiddleDot} Updated: {msgListUpdateTime}')    #: Hazırlık sonu mesajı.
            except:                                                             ## Hata alınması durumunda yapıalcak işlemler.
                txtLog(f'{preLogErr}Liste bilgileri çekilirken hata.')          #: Log dosyasına hata hakkında bilgi yazdırılıyor.
        else:                                                                                                   ## Diğer imzayı istemesi durumunda.
            print(f'\n{preCmdMiddleDot} Filename: {open_csv}')                                                  #: CSV dosyasının ismi hakkında ekrana bilgi yazdırılır.
            print(f'{preCmdMiddleDot} Film sayısı: {loopCount-1}')                                              #: Film sayısı hakkında ekrana bilgi yazdırılır.
            print(f'{preCmdMiddleDot} Tüm filmler {cmdBlink(open_csv,"yellow")} dosyasına aktarıldı.')          #: Filmerin hangi CSV dosyasına aktarıldığı ekrana yazdırılır.
            try:                                                                                                ## Seçili olan filtreleri ekrana yazdırabilmek için işlemler.
                search_selected_decadeyear = currentDom.select(".smenu-subselected")[3].text                    #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                search_selected_genre = currentDom.select(".smenu-subselected")[2].text                         #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                search_selected_sortby = currentDom.select(".smenu-subselected")[0].text                        #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                                                                                                                ## Ekrana yazdırmalar.
                print(f'{preCmdMiddleDot} Filtered as {search_selected_decadeyear} movies only was done by')    #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
                print(f'{preCmdMiddleDot} Filtered as {search_selected_genre} only movies')                     #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
                print(f'{preCmdMiddleDot} Movies sorted by {search_selected_sortby}')                           #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
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
        
        try: #: meta etiketinden veri almayı dener eğer yoksa liste değil.
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
        except: #: liste imzası olmadığı belirlenir.
            print(f'{preBlankCount}List not found.')
            currentUrl = ''
            currentListAvaliable = False
    except:
        currentListAvaliable = False
    finally:
        return currentListAvaliable, currentUrl

def test_pause(): #: Geliştirici duraklatmaları için kalıp.
    os.system('echo Test için durduruluyor. & pause >nul')

def cmdPre(m,c): #: Mesaj ön ekleri için kalıp.
    return f'[{colored(m,color=c)}]'

def cmdBlink(m,c):
    return colored(m,c,attrs=["blink"])
    
# > cprint ASCII Okuyabilmesi için program başlarken bir kere color kullanıyoruz: https://stackoverflow.com/a/61684844
# > Sonrasında hem temiz bir başlangıç hem de yeniden başlatmalarda Press any key.. mesajını kaldırmak için cls.
cmdRunTime = datetime.now().strftime('%d%m%Y%H%M%S') #: Run time check - Generate session hash
os.system(f'color & cls & title Welcome %USERNAME%.')
# siteProtocol, siteUrl = "https://", "letterboxd.com/"     # Saf domain'in parçalanarak birleştirilmesi
# siteDomain = siteProtocol + siteUrl                       # Saf domain'in parçalanarak birleştirilmesi
## Mesajlar, Log Mesaj atamaları
# Cmd
preCmdInput = cmdPre(">","green")
preCmdErr = cmdPre("!","red")
preCmdInfo = cmdPre("#","yellow")
preCmdMiddleDot = cmdPre(u"\u00B7","cyan") # middle dot
preBlankCount = 4*' '
# Log
preLogInfo = "Bilgi: "
preLogErr = "Hata: "
# Messages
msgCancel = "The session was canceled because you did not verify the information."

print(f'{preCmdInfo} Session hash: {cmdBlink(cmdRunTime,"yellow")}') #: Oturum için farklı bir isim üretildi.
logDirName, exportDirName = settingsFileSet()
logFilePath = f'{logDirName}/{cmdRunTime}.txt' #: logging, dircheck
dirCheck([logDirName]) # Log file check
open_csv = f'{exportDirName}/{cmdRunTime}.csv' 

while True:
    listUrl = str(input(f'{preCmdInput} List Url: ')).lower() #: List url alındı ve str küçültüldü.
    visitUserListUrl = listUrl
    visitList = doReadPage(visitUserListUrl)
    userListAvailable, approvedListUrl = userListCheck() #: Liste mevcutluğu kontrol ediliyor.
    if userListAvailable:
        editedListVisitUrl = f'{approvedListUrl}detail/' # Guest generate url. approvedListUrl https://letterboxd.com/username/list/listname/
        soup = doReadPage(editedListVisitUrl)
        url = f'{editedListVisitUrl}page/'
        # Karşılama mesajı, kullanıcının girdiği bilgleri ve girilen bilgilere dayanarak listenin bilgilerini yazdırır.
        signature(1)
        # > Domain'in doğru olup olmadığı kullanıcıya sorulur, doğruysa kullanıcı enter'a basar ve program verileri çeker.
        print(f'{preCmdMiddleDot} Link: {editedListVisitUrl}')
        ent = input(f'\n{preCmdInput} Press enter to confirm the entered information. (Enter)')
        if ent == "":
            print(f'{preBlankCount}{colored("List confirmed.", color="green")}')
            txtLog(f'{preLogInfo}Saf sayfaya erişim başlatılıyor.')
            soup = doReadPage(editedListVisitUrl) #: Verinin çekileceği dom'a filtre ekleniyor.
            lastPageNo = getListLastPageNo()
            dirCheck([exportDirName]) #: Export klasörünün kontrolü.
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
        break