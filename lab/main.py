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

def dirCheck(dirs): # List
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

def doReadPage(tempUrl): #: Url'si belirtilen sayfanın okunup, dom alınması.
    try:
        txtLog(f'{preLogInfo}Trying connect to [{tempUrl}]')                            #: Log dosyasına bağlantı başlangıcında bilgi veriliyor.
        urlResponseCode = requests.get(tempUrl)                                         #: Get response code.
        urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')  #: Get page dom.               
        return urlDom                                                                   #: Return page dom.
    except:                                                                             #: Dom edinirken hata gerçekleşirse..
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
    try:                                                                                                                                ## Listenin son sayfa işlemleri.
        lastPageDom = doReadPage(f'{url}{tempLastPageNo}')                                                                              #: Getting lastpage dom.
        lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li") #: Sayfa kodları çekildi.
        lastPageMoviesCount =  len(lastPageArticles)                                                                                    #: Film sayısı öğrenildi.
        movieCount = ((int(tempLastPageNo)-1)*100)+lastPageMoviesCount                                                                  #: Toplam film sayısını belirlemek.
        txtLog(f"{preLogInfo}Listedeki film sayısı {movieCount} olarak bulunmuştur.")                                                   #: Film sayısı hesaplandıktan sonra ekrana yazdırılır.
        return movieCount                                                                                                               #: Film sayısı çağrıya gönderilir.
    except:                                                                                                                             ## Olası hata durumunda.
        print(f'Error getting movie count.')
        txtLog(f'{preLogErr}An error occurred while obtaining the number of movies.')

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
                print('The settings file could not be found. Please enter the required information.')
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
                print(f'Your settings could not be saved due to {msgExcept}.')
    return logDirName, exportDirName

def signature(x): #: x: 0 start msg, 1 end msg
    try:
        if x == True:                                                           ## İmza seçimi bu olması durumunda.
            try:                                                                ## Liste sayfasından bilgiler çekmek.
                print(f"\nProcess No: ({len(urlList)}/{processLoopNo})")
                print(colored('List info;', color="yellow"))                    #: Liste başlığı.
                                                                                ## Liste bilgileri alınır.
                listBy = soup.select("[itemprop=name]")[0].text                 #: Liste sahibin ismini çekiliyor.
                listTitle = soup.select("[itemprop=title]")[0].text.strip()     #: Liste başlığının ismini çekiliyor.
                listPublicationTime = soup.select(".published time")[0].text    #: Liste oluşturulma tarihi çekiliyor.
                listPT = arrow.get(listPublicationTime)                         #: Liste oluşturulma tarihi düzenleniyor. Arrow: https://arrow.readthedocs.io/en/latest/
                listMovieCount =  getMovieCount(getListLastPageNo())            #: Listedeki film sayısı hesaplanıyor.
                                                                                ## Liste bilgileri yazdırılır.
                print(f'{preCmdMiddleDot} List Url: {currentUrListItem}')       #: List URL                              
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
                domSelectedDecadeYear = currentDom.select(".smenu-subselected")[3].text                    #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                domSelectedGenre = currentDom.select(".smenu-subselected")[2].text                         #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                domSelectedSortBy = currentDom.select(".smenu-subselected")[0].text                        #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                                                                                                                ## Seçili filtreleri ekrana yazdırmalar.
                print(f'{preCmdMiddleDot} Filtered as {domSelectedDecadeYear} movies only was done by')    #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
                print(f'{preCmdMiddleDot} Filtered as {domSelectedGenre} only movies')                     #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
                print(f'{preCmdMiddleDot} Movies sorted by {domSelectedSortBy}')                           #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
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
            metaOgType = getMetaContent('og:type') 
            # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşılır.
            if metaOgType == "letterboxd:list":
                txtLog(f'{preLogInfo}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {metaOgType}')
                metaOgUrl = getMetaContent('og:url')                                    #: Liste yönlendirmesi var mı bakıyoruz
                metaOgTitle = getMetaContent('og:title')                             #: Liste ismini alıyoruz.
                bodyDataOwner = urlListItemDom.find('body').attrs['data-owner']                                              #: Liste sahibinin kullanıcı ismi.
                print(f'{preBlankCount}{colored("Found it: ", color="green")}@{bodyDataOwner} "{metaOgTitle}"')          #: Liste sahibinin kullanıcı ismi ve liste ismi ekrana yazdırılır.
                if metaOgUrl == urlListItem:
                    txtLog(f'{preLogInfo}Liste adresi yönlendirme içermiyor.')
                else:
                    #print(f'[{colored("!", color="yellow")}] Girdiğiniz liste linki eskimiştir, muhtemelen liste ismi yakın bir zamanda değişildi.')
                    print(f'{preBlankCount}{colored(urlListItem, color="yellow")} adresini değiştirdik.')
                    print(f'{preBlankCount}{colored(metaOgUrl, color="green")} adresinden devam ediyoruz.')
                txtLog(f'{preLogInfo}{urlListItem} listesi bulundu: {metaOgTitle}')
                currentListAvaliable = True
        except Exception as e: #: liste imzası olmadığı belirlenir.
            print(f'{preBlankCount}List not found.', e)
            metaOgUrl = ''
            currentListAvaliable = False
    except:
        currentListAvaliable = False
    finally:
        return currentListAvaliable, metaOgUrl

def test_pause(): #: Geliştirici duraklatmaları için kalıp.
    os.system('echo Test için durduruluyor. & pause >nul')

def cmdPre(m,c): #: Mesaj ön ekleri için kalıp.
    return f'[{colored(m,color=c)}]'

def cmdBlink(m,c):
    return colored(m,c,attrs=["blink"])
    
def getRunTime():
    return datetime.now().strftime('%d%m%Y%H%M%S')

def getMetaContent(_):
    return urlListItemDom.find('meta', property=_).attrs['content']

def getBodyOwner():
    return urlListItemDom.find('body').attrs['data-owner']

def getItCleanAfter(_):
    return currentUrListItem[currentUrListItem.index(_)+len(_):].replace('/',"")

# > cprint ASCII Okuyabilmesi için program başlarken bir kere color kullanıyoruz: https://stackoverflow.com/a/61684844
# > Sonrasında hem temiz bir başlangıç hem de yeniden başlatmalarda Press any key.. mesajını kaldırmak için cls.
 #: Run time check - Generate session hash

# siteProtocol, siteUrl = "https://", "letterboxd.com/"     #: Saf domain'in parçalanarak birleştirilmesi
# siteDomain = siteProtocol + siteUrl                       #: Saf domain'in parçalanarak birleştirilmesi

msgCancel = "The session was canceled because you did not verify the information."  #: Cancel msg
msgUrlErr = "Enter a different URL, it's already entered. You can end the login by putting a period at the end of the url."
preCmdMiddleDot = cmdPre(u"\u00B7","cyan")                                          #: Cmd middle dot pre
preCmdInput = cmdPre(">","green")                                                   #: Cmd input msg pre
preCmdInfo = cmdPre("#","yellow")                                                   #: Cmd info msg pre
preCmdErr = cmdPre("!","red")                                                       #: Cmd error msg pre
preBlankCount = 4*' '                                                               #: Cmd msg pre blank calc
preLogInfo = "Bilgi: "                                                              #: Log file ingo msg pre
preLogErr = "Hata: "                                                                #: Log file err msg pre
sessionHash = getRunTime()                                                          #: Generate start hash
logDirName, exportDirName = settingsFileSet()                                       #: Set Export dir and Log dir
logFilePath = f'{logDirName}/{sessionHash}.txt'                                     #: Set log file dir
dirCheck([logDirName]) # Log file check

while True:
    os.system(f'color & cls & title Welcome %USERNAME%.')
    print(f'{preCmdInfo} Session hash: {cmdBlink(sessionHash,"yellow")}')                #: Oturum için farklı bir isim üretildi.
    urlList = []
    inputLoopNo = 0 
    processLoopNo = 0

    while True:
        inputLoopNo += 1
        urlListItem = str(input(f'{inputLoopNo})  List URL (Press ENTER to end the entry): ')).lower()  #: List url alındı ve str küçültüldü.
        if len(urlListItem) > 0:                                                                        #: No Blank
            if urlListItem == ".":                                                                      
                break
            else:
                pass
            urlListItemDom = doReadPage(urlListItem)
            userListAvailable, approvedListUrl = userListCheck()                                        #: Liste mevcutluğu kontrol ediliyor.
            if userListAvailable: 
                if urlListItem[-1] == ".":
                    if urlListItem not in urlList:
                        urlList.append(approvedListUrl) # adding the element
                        print("Url alımı tamamlandı. Sonraki işleme geçiliyor.")
                        break
                    else:
                        print(msgUrlErr)
                        inputLoopNo -= 1
                else:
                    if urlListItem not in urlList:
                        urlList.append(approvedListUrl) # adding the element
                    else:
                        print(msgUrlErr)
                        inputLoopNo -= 1
            else:
                pass
        else:
            pass

    for currentUrListItem in urlList:
        processLoopNo += 1
        open_csv = f"{exportDirName}/{getRunTime()}_{getBodyOwner()}_{getItCleanAfter('/list/')}.csv" 
        editedUrlListItem = f'{currentUrListItem}detail/' # Guest generate url. approvedListUrl https://letterboxd.com/username/list/listname/
        soup = doReadPage(editedUrlListItem)
        url = f'{editedUrlListItem}page/'
        # Karşılama mesajı, kullanıcının girdiği bilgleri ve girilen bilgilere dayanarak listenin bilgilerini yazdırır.
        signature(1)
        # > Domain'in doğru olup olmadığı kullanıcıya sorulur, doğruysa kullanıcı enter'a basar ve program verileri çeker.
        print(f'{preCmdMiddleDot} Link: {editedUrlListItem}')
        ent = input(f'\n{preCmdInput} Press enter to confirm the entered information. (Enter)')
        if ent == "":
            print(f'{preBlankCount}{colored("List confirmed.", color="green")}')
            txtLog(f'{preLogInfo}Saf sayfaya erişim başlatılıyor.')
            soup = doReadPage(editedUrlListItem) #: Verinin çekileceği dom'a filtre ekleniyor.
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
        else:
            print(msgCancel)
            txtLog(preLogInfo + msgCancel)
