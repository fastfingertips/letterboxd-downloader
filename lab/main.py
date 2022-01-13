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
from inspect import currentframe

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
    except Exception as e:
        if cmdLogOnOff:
            errorLine(e)  
            txtLog('An error was encountered while obtaining movie information.')

def doReadPage(tempUrl): #: Url'si belirtilen sayfanın okunup, dom alınması.
    try:
        txtLog(f'{preLogInfo}Trying connect to [{tempUrl}]')                            #: Log dosyasına bağlantı başlangıcında bilgi veriliyor.
        urlResponseCode = requests.get(tempUrl)                                         #: Get response code.
        urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')  #: Get page dom.               
        return urlDom                                                                #: Return page dom.
    except Exception as e:
        if cmdLogOnOff:
            errorLine(e)                                                                #: Dom edinirken hata gerçekleşirse..
            txtLog(f'{preLogErr}Connection to address failed [{tempUrl}]')

def doReset():  # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except Exception as e:
        if cmdLogOnOff:
            errorLine(e)  
            txtLog(preLogErr + 'Attempting to restart the program failed.')

def getListLastPageNo():  # Listenin son sayfasını öğren
    try:
        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
        txtLog(f'{preLogInfo}Listedeki sayfa sayısı denetleniyor..')
        lastPageNo = soup.find('div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text    # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        txtLog(f'{preLogInfo}Liste birden çok sayfaya ({lastPageNo}) sahiptir.')
        getMovieCount(lastPageNo)
    except AttributeError:                                                                            ## Kontrolümüzde..
        txtLog(f'{preLogInfo}Birden fazla sayfa yok, bu liste tek sayfadır.',AttributeError)                   
        lastPageNo = 1                                                                          #: Sayfa sayısı bilgisi alınamadığında sayfa sayısı 1 olarak işaretlenir.
        getMovieCount(lastPageNo)                                                               #: Sayfa bilgisi gönderiliyor.
    except Exception as e:
        if cmdLogOnOff:
            errorLine(e)                                                             
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
    except Exception as e:
        if cmdLogOnOff:
            errorLine(e)          
            txtLog(f'Error getting movie count.')                                                      #: Dom edinirken hata gerçekleşirse..                                                                                                                        ## Olası hata durumunda.
            txtLog(f'{preLogErr}An error occurred while obtaining the number of movies.')

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
                    txtLog(f'Ayarlarınız {e} nedeniyle alınamadı.')
    else:
        while True:
            try:
                print(f'{preCmdErr} The settings file could not be found. Please enter the required information.')
                logDirName = input(f'{preCmdInput} Log directory Name: ')
                exportDirName = input(f'{preCmdInput} Export directory Name: ')
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
                    txtLog(f'Your settings could not be saved due to {e}.')
    return logDirName, exportDirName

def signature(x): #: x: 0 start msg, 1 end msg
    try:
        if x == True:                                                                                       ## Kullanıcı tarafından belirlen imza seçimi bu olması durumunda.
            try:                                                                                            ## Liste sayfasından bilgiler çekmek.
                print(f"\nProcess No: ({len(urlList)}/{processLoopNo})")                                    #: İşlem durumu, sırası ekrana bastırılır.
                print(colored('List info;', color="yellow"))                                                #: Liste başlığı.
                                                                                                            ## Liste bilgileri alınır.
                listBy = soup.select("[itemprop=name]")[0].text                                             #: Liste sahibin ismini çekiliyor.
                listTitle = soup.select("[itemprop=title]")[0].text.strip()                                 #: Liste başlığının ismini çekiliyor.
                listPublicationTime = soup.select(".published time")[0].text                                #: Liste oluşturulma tarihi çekiliyor.
                listPT = arrow.get(listPublicationTime)                                                     #: Liste oluşturulma tarihi düzenleniyor. Arrow: https://arrow.readthedocs.io/en/latest/
                listMovieCount =  getMovieCount(getListLastPageNo())                                        #: Listedeki film sayısı hesaplanıyor.
                
                print(supLine)                                                                                            ## Liste bilgileri yazdırılır.
                print(f'{preCmdMiddleDot} List by {listBy}')                                                # Liste sahibinin görünen adı yazdırılıyor.
                print(f'{preCmdMiddleDot} List title: {listTitle}')                                         #: Liste başlığı yazdırılıyor.
                print(f'{preCmdMiddleDot} Number of movies: {listMovieCount}')                              #: Listede bulunan film sayısı yazdırılıyor.
                print(f'{preCmdMiddleDot} Published: {listPT.humanize()}')                                  #: or print(f'Published: {listPtime.humanize(granularity=["year","month", "day", "hour", "minute"])}')
                print(f'{preCmdMiddleDot} List URL: {currentUrListItem}')                                   #: List URL                              
                print(f'{preCmdMiddleDot} Process URL: {editedUrlListItem}')                                #: İşlem görecek URL ekrana bastırılır.
                try:                                                                                        ## Search list update time
                    listUpdateTime = soup.select(".updated time")[0].text                                   #: Liste düzenlenme vakti çekiliyor.
                    listUT = arrow.get(listUpdateTime)                                                      #: Çekilen liste düzenlenme vakti düzenleniyor.
                    msgListUpdateTime = listUT.humanize()                                                   #: Çekilen liste düzenlenme vakti kullanıma hazırlanıyor.
                except Exception as e:
                    if cmdLogOnOff:
                        errorLine(e)                                                                                     ## Hata alınırsa liste düzenlenmemiş varsayılır.
                    msgListUpdateTime = 'No editing.'                                                       #: Liste düzenlenmemiş.
                finally:                                                                                    ## Kontrol sonu işlemleri.
                    print(f'{preCmdMiddleDot} Updated: {msgListUpdateTime}')                                #: Hazırlık sonu mesajı.
                    print(subLine)
            except Exception as e:
                if cmdLogOnOff:
                    errorLine(e)                                                                                        ## Hata alınması durumunda yapıalcak işlemler.
                    txtLog(f'{preLogErr}Liste bilgileri çekilirken hata.')                                      #: Log dosyasına hata hakkında bilgi yazdırılıyor.
        else:         
            print(supLine)
            print(f'{preCmdMiddleDot} Tüm filmler {cmdBlink(openCsv,"yellow")} dosyasına aktarıldı.')       #: Filmerin hangi CSV dosyasına aktarıldığı ekrana yazdırılır.
            print(f'{preCmdMiddleDot} Filename: {openCsv}')                                               #: CSV dosyasının ismi hakkında ekrana bilgi yazdırılır.
            print(f'{preCmdMiddleDot} Film sayısı: {loopCount-1}')                                          #: Film sayısı hakkında ekrana bilgi yazdırılır.
            try:                                                                                            ## Seçili olan filtreleri ekrana yazdırabilmek için işlemler.
                domSelectedDecadeYear = currentDom.select(".smenu-subselected")[3].text                     #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                domSelectedGenre = currentDom.select(".smenu-subselected")[2].text                          #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                domSelectedSortBy = currentDom.select(".smenu-subselected")[0].text                         #: Liste sayfasından ilgili filtre bilgisi alınıyor.
                                                                                                            ## Seçili filtreleri ekrana yazdırmalar.
                print(f'{preCmdMiddleDot} Filtered as {domSelectedDecadeYear} movies only was done by')     #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
                print(f'{preCmdMiddleDot} Filtered as {domSelectedGenre} only movies')                      #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
                print(f'{preCmdMiddleDot} Movies sorted by {domSelectedSortBy}')                            #: Liste sayfasından alınan ilgili filtre bilgisi yazdırılıyor
                print(subLine)
            except Exception as e:
                if cmdLogOnOff:
                    errorLine(e)                                                                                           ## Filtre bilgileri edinirken bir hata oluşursa..
                    txtLog(f'{preLogErr}Film filtre bilgileri alınamadı..')                                     #: Log dosyasına hata bilgisi verilir.
        log = f'{preLogInfo}İmza yazdırma işlemleri tamamlandı.'                                            #: İmza sonu log bilgisi işlenir.
    except Exception as e: #: İmza seçimi başarısız.
        if cmdLogOnOff:
            errorLine(e)                                                                                     #: Duruma bağlı cmd ekran bilgisi                                                               #: Ekrana bilgi.
        log = f'{preLogErr}İmza yüklenemedi. Program yine de devam etmeyi deneyecek.'                       #: Log dosyasına yazılacak bilgi aktarması.
    finally:                                                                                                ## Seçili imza sonunda uygulanacaklar..
        txtLog(log)                                                                                         #: Log dosyasına bilgi verilir.

def txtLog(r_message, r_loglocation=None):                                                                  #: None: Kullanıcı log lokasyonunu belirtmese de olur.
    try:                                                                                                    ## Denenecek işlemler..
        f = open(logFilePath, "a")                                                                          #: Eklemek üzere bir dosya açar, mevcut değilse dosyayı oluşturur
        f.writelines(f'{r_message}\n')                                                                      #:
        f.close()                                                                                           #:
    except Exception as e:                                                                                ## 
        if r_loglocation is not None:                                                                       ##
            print(f'Loglama işlemi {r_loglocation} konumunda {e} nedeniyle başarısız.')                     #:
        else:                                                                                               ##
            print(f'Loglama işlemi {e} nedeniyle başarısız.')                                               #:

def userListCheck(): #: Kullanıcının girilen şekilde bir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        try: #: meta etiketinden veri almayı dener eğer yoksa liste değil.
            metaOgType = getMetaContent('og:type') 

            if metaOgType == "letterboxd:list":                                                                                 # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşılır.
                txtLog(f'{preLogInfo}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {metaOgType}')
                metaOgUrl = getMetaContent('og:url')                                                                            #: Liste yönlendirmesi var mı bakıyoruz
                metaOgTitle = getMetaContent('og:title')                                                                        #: Liste ismini alıyoruz.
                bodyDataOwner = getBodyOwner()                                                                                  #: Liste sahibinin kullanıcı ismi.

                print(f'{preBlankCount}{colored("Found it: ", color="green")}@{colored(bodyDataOwner,"yellow")} "{colored(metaOgTitle,"yellow")}"')          #: Liste sahibinin kullanıcı ismi ve liste ismi ekrana yazdırılır.
                if urlListItem == metaOgUrl:                                                                                    #: Girilen URL Meta ile aynıysa..
                    txtLog(f'{preLogInfo}Liste adresi yönlendirme içermiyor.')                                                  #: Log'a bilgi ver.
                else:
                    if cmdLogOnOff:                                                                                             #: Girilen URL Meta ile uyuşmuyorsa..
                        print(f'{preCmdInfo} Girdiğiniz liste linki yönlendirme içeriyor, muhtemelen liste ismi yakın bir zamanda değişildi veya hatalı girdiniz.')
                    print(f'{preBlankCount}({colored("+","red")}): {colored(urlListItem, color="yellow")} adresini')
                    if urlListItem in metaOgUrl:                                                                                #:
                        msgInputUrl = colored(urlListItem, color="yellow")
                        msgMetaOgUrlChange = colored(metaOgUrl.replace(urlListItem,""), color="green")
                    else:
                        metaLoop = len(metaOgUrl)
                        msgMetaOgUrlChange = ''
                        msgInputUrl = ''
                        for i in range(metaLoop):
                                # print(urlListItem[i], metaOgUrl[i], urlListItem[i]==metaOgUrl[i]) #: Dev test
                                if urlListItem[i] == metaOgUrl[i]:
                                    msgMetaOgUrlChange += colored(metaOgUrl[i], color="yellow")
                                else:
                                    msgMetaOgUrlChange += colored(metaOgUrl[i], color="green")
                    print(f'{preBlankCount}({colored("+","green")}): {msgInputUrl}{msgMetaOgUrlChange} şeklinde değiştirdik.')
                txtLog(f'{preLogInfo}{urlListItem} listesi bulundu: {metaOgTitle}')
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
    os.system(f"echo {preCmdInfo} {cmdBlink('Enter to continue.','yellow')} & pause >nul")

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
    return txtLog(currentUrListItem[currentUrListItem.index(_)+len(_):].replace('/',""))

# Error Code generator
def errorLine(e):
    cl = currentframe()
    txtLog(f'{preLogErr} Error on line {cl.f_back.f_lineno} Exception Message: {e}')
# > cprint ASCII Okuyabilmesi için program başlarken bir kere color kullanıyoruz: https://stackoverflow.com/a/61684844
# > Sonrasında hem temiz bir başlangıç hem de yeniden başlatmalarda Press any key.. mesajını kaldırmak için cls.

supLine = '¯'*30                                                                                      ## Diğer imzayı istemesi durumunda.
subLine = '_'*30   
msgDevBug = 'An uncontrolled error has occurred. Please notify the developer.'      #: Kontrolsüz hataların oluştuğu yerlerde kullanılır.
msgCancel = "The session was canceled because you did not verify the information."  #: Cancel msg
msgUrlErr = "Enter a different URL, it's already entered. You can end the login by putting a period at the end of the url."
siteProtocol, siteUrl = "https://", "letterboxd.com/"                               #: Saf domain'in parçalanarak birleştirilmesi
siteDomain = siteProtocol + siteUrl                                                 #: Saf domain'in parçalanarak birleştirilmesi
cmdLogOnOff = True                                                                  #: Cmd ekran bildirmeleri
settingsFileName = 'settings'+'.json'
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
dirCheck([logDirName])                                                              #: Log file check   



while True:
    os.system(f'color & cls & title Welcome %USERNAME%.')                           #: İlk başlangıç ve yeni başlangıçlara hazırlık.
    print(f'{preCmdInfo} Session hash: {cmdBlink(sessionHash,"yellow")}')           #: Oturum için farklı bir isim üretildi.
    urlList = []
    breakLoop = False
    inputLoopNo = 0 
    processLoopNo = 0

    while True:
        inputLoopNo += 1                                                                                                            #: Başlangıçta döngü değerini artırıyoruz.  (Konum bilgisi)
        urlListItem = str(input(f'{preCmdInput} List URL[{inputLoopNo}]: ')).lower()                                                #: List url alındı ve str küçültüldü.       (Alım ve Düzenleme)
        if len(urlListItem) > 0:                                                                                                    ## Giriş boş değilse..                      (Kontrol)                                   
            if urlListItem == ".":                                                                                                  ## Url girişi yerine nokta girildiyse..     (Kontrol)
                break                                                                                                               #: Nokta girişi son bulma emri alınır.      (Emir)
            elif urlListItem[-1] == ".":                                                                                            ## Girilen url sonunda nokta varsa..        (Kontrol)
                breakLoop = True                                                                                                    #: Url alımını sonlandıracak bilgi.         (Emir)
                while urlListItem[-1] == ".":                                                                                       #: Url sonunda nokta olduğu sürece.         (Devamlı kontrol) 
                        urlListItem = urlListItem[:len(urlListItem)-1]                                                              #: Her defasında Url sonundan nokta siler.  (Düzen aktarma)
            urlListItemDom = doReadPage(urlListItem)                                                                                #: Sayfa dom'u alınır.
            userListAvailable, approvedListUrl = userListCheck()                                                                    #: Liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
            if userListAvailable:                                                                                                   #: Liste kullanıma uygunsa..
                if approvedListUrl not in urlList:                                                                                  #: Doğrulanmış URL daha önce URL Listesine eklenmediyse..
                    urlList.append(approvedListUrl)                                                                                 #: Doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
                    if breakLoop:                                                                                                   #: Kullanıcı URL sonunda nokta belirttiyse bu url sonrası alım sonlanır ve sonraki işlemlere geçilir.
                        print(f"{preBlankCount}{colored('Url acquisition completed. Moving on to the next steps.','green')}")       #: URL alımının sonlandığı bilgisini ekrana yazdırıyoruz.
                        break                                                                                                       #: URL alımını sonlandırıyoruz. Döngüden çıktık.
                else:                                                                                                               ## Doğrulanmış URL daha önce işlem görecek URL listine eklenmiş ise..
                    print(f'{preCmdErr} You have already entered this address list.')                                               #: URL'in daha önce girildiğini ekrana yazdırıyoruz.
                    inputLoopNo -= 1                                                                                                #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
            else:                                                                                                                   ## Kullanıcının girdiği URL doğrulanmazsa..
                print(f"{preCmdInfo} You did not enter a valid url.")                                                               #: Kullanıcının url'i doğrulanmadığında bilgilendirilir.
                inputLoopNo -= 1                                                                                                    #: Başarısız girişlerde döngü sayısının normale çevrilmesi.
        else:                                                                                                                       ## Kullanıcı genişliğe sahip bir değer girmez ise..
            print(f"{preCmdInfo} Just enter a period to move on to the next steps. You can also add it at the end of the URL.")
            inputLoopNo -= 1                                                                                                        #: Başarısız girişlerde döngü sayısının normale çevrilmesi.

    for currentUrListItem in urlList:
        processLoopNo += 1
        openCsv = f"{exportDirName}/{getRunTime()}_{getBodyOwner()}_{getItCleanAfter('/list/')}.csv" 
        editedUrlListItem = f'{currentUrListItem}detail/' # Guest generate url. approvedListUrl https://letterboxd.com/username/list/listname/
        soup = doReadPage(editedUrlListItem)
        url = f'{editedUrlListItem}page/'
        # Karşılama mesajı, kullanıcının girdiği bilgleri ve girilen bilgilere dayanarak listenin bilgilerini yazdırır.
        signature(1)
        # > Domain'in doğru olup olmadığı kullanıcıya sorulur, doğruysa kullanıcı enter'a basar ve program verileri çeker.
        ent = input(f'\n{preCmdInput} Press enter to confirm the entered information. (Enter)')
        if ent == "":
            print(f'{preBlankCount}{colored("List confirmed.", color="green")}')
            txtLog(f'{preLogInfo}Saf sayfaya erişim başlatılıyor.')
            soup = doReadPage(editedUrlListItem) #: Verinin çekileceği dom'a filtre ekleniyor.
            lastPageNo = getListLastPageNo()
            dirCheck([exportDirName]) #: Export klasörünün kontrolü.
            with open(openCsv, 'w', newline='', encoding="utf-8") as csvFile: #: Konumda Export klasörü yoksa dosya oluşturmayacaktır.
                writer = csv.writer(csvFile)
                writer.writerow(["Title", "Year"])
                # Filmleri çekiyoruz
                loopCount = 1
                # x sıfırdan başlıyor
                print("\nMovies on the list:")
                for x in range(int(lastPageNo)):
                    txtLog(f'Connecting to: {url}{str(x+1)}')
                    currentDom = doReadPage(f'{url}{str(x+1)}')
                    loopCount = doPullFilms(loopCount, currentDom)
                # Açtığımız dosyayı manuel kapattık
                csvFile.close()
            txtLog(f'{preLogInfo}Success!')
            signature(0)
        else:
            print(msgCancel)
            txtLog(preLogInfo + msgCancel)
    test_pause()
