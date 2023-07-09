from log_methods import txtLog, errorLine
from color_methods import preCmdErr, preCmdInfo
from constants import *
import requests
from bs4 import BeautifulSoup as bs #: BeautifulSoup

def getMetaContent(dom, obj):
    try: metaContent = dom.find('meta', property=obj).attrs['content']
    except AttributeError:
        print(f"{preCmdErr}Meta etiketinden '{obj}' alınamadı.")
        # txtLog(f"Meta etiketinden '{obj}' alınamadı. Hata Mesajı: {AttributeError}", logFilePath)
        metaContent = ''
    return metaContent

def getBodyContent(dom, obj):
    return dom.find('body').attrs[obj]

def getMovieCount(tempLastPageNo, cListDom, currentUrListItemDetailPage): # Film sayısını öğreniyoruz
    try:
        try: # Son sayfaya bağlanıp, son sayfadaki film sayısını almak bir get isteği üretir ve programı yavaşlatır bu nedenle bir alternatif
            metaDescription = cListDom.find('meta', attrs={'name':'description'}).attrs['content']
            metaDescription = metaDescription[10:] #: açıklama kısmındaki 'A list of ' sonrası
            for i in range(6):
                try:
                    int(metaDescription[i])
                    ii = i+1
                except: pass
            movieCount = metaDescription[:ii]
        except Exception as e: ## Listenin son sayfa işlemleri.
            lastPageDom = doReadPage(f'{currentUrListItemDetailPage}{tempLastPageNo}') #: Getting lastpage dom.
            lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li") #: Sayfa kodları çekildi.
            lastPageMoviesCount =  len(lastPageArticles) #: Film sayısı öğrenildi.
            movieCount = ((int(tempLastPageNo)-1)*100)+lastPageMoviesCount #: Toplam film sayısını belirlemek.
            # txtLog(f"{PRE_LOG_INFO}Listedeki film sayısı {movieCount} olarak bulunmuştur.",logFilePath) #: Film sayısı hesaplandıktan sonra ekrana yazdırılır.
        return movieCount #: Film sayısı çağrıya gönderilir.
    except Exception as e: ## Olası hata durumunda. (Dom edinirken)
        errorLine(e)
        # txtLog('Error getting movie count.', logFilePath)
        # txtLog(f'{PRE_LOG_ERR}An error occurred while obtaining the number of movies.',logFilePath)

def doReadPage(tempUrl): #: Url'si belirtilen sayfanın okunup, dom alınması.
    try:
        #txtLog(f'{PRE_LOG_INFO}Trying connect to [{tempUrl}]',logFilePath) #: Log dosyasına bağlantı başlangıcında bilgi veriliyor.
        while True:
            #: https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                urlResponseCode = requests.get(tempUrl,timeout=30)
                urlDom = bs(urlResponseCode.content.decode('utf-8'), 'html.parser')
                if urlDom != None: return urlDom #: Return page dom
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.")
                print(str(e))
                continue
            except requests.Timeout as e:
                print("OOPS!! Timeout Error")
                print(str(e))
                continue
            except requests.RequestException as e:
                print("OOPS!! General Error")
                print(str(e))
                continue
            except KeyboardInterrupt: print("Someone closed the program")
            except Exception as e: print('Hata:',e)
    except Exception as e: #: Dom edinirken hata gerçekleşirse..
        errorLine(e)
        # txtLog(f'{PRE_LOG_ERR}Connection to address failed [{tempUrl}]',logFilePath)

def getListLastPageNo(cListDom, currentUrListItemDetailPage): # Listenin son sayfasını öğren
    try:
        # Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al. Son'linin içindeki bağlantının metni bize kaç sayfalı bir listemiz olduğunuz verecek.
        # txtLog(f'{PRE_LOG_INFO}Listedeki sayfa sayısı denetleniyor..',logFilePath)
        lastPageNo = cListDom.find('div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        # txtLog(f'{PRE_LOG_INFO}Liste birden çok sayfaya ({lastPageNo}) sahiptir.',logFilePath)
        getMovieCount(lastPageNo, cListDom, currentUrListItemDetailPage)
    except AttributeError: ## Kontrolümüzde..
        # txtLog(f'{PRE_LOG_INFO}Birden fazla sayfa yok, bu liste tek sayfadır. {AttributeError}',logFilePath)
        lastPageNo = 1 #: Sayfa sayısı bilgisi alınamadığında sayfa sayısı 1 olarak işaretlenir.
        getMovieCount(lastPageNo) #: Sayfa bilgisi gönderiliyor.
    except Exception as e: errorLine(e)
    finally:
        # txtLog(f'{PRE_LOG_INFO}Sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPageNo} olduğu öğrenildi.',logFilePath)
        return lastPageNo

def doPullFilms(tempLoopCount, tempCurrentDom, writer): # Filmleri çekiyoruz yazıyoruz
    try:
        #> Filmleri/Posterleri içeren kapsayıcının çekimi (<ul> elemanı)
        filmDetailsList = tempCurrentDom.find('ul', attrs={'class': 'js-list-entries poster-list -p70 film-list clear film-details-list'})
        #> Yukarıda edinmeye çalışılan kapsayıcının(<ul> elemanı) boş olması durumunda alternatif yollar denenmiş, eşleşememenin önüne geçilmeye çalışılmıştır.
        for currentAlternative in ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']:
            if filmDetailsList is None: filmDetailsList = tempCurrentDom.select_one(currentAlternative)
            else: 
                print(f'{preCmdInfo}{tempLoopCount} ve sonrası için film/poster kapsayıcısı alternatif yardımı gerekmeksizin çekildi.')
                break
        else:
            if filmDetailsList is None: print(f'{preCmdInfo}{tempLoopCount} ve sonrası için film/poster kapsayıcısı çekilemedi.')
            else: print(f'{preCmdInfo}{tempLoopCount} ve sonrasi için film/poster kapsayıcısı alternatif yardımıyla çekildi.')
        #> Kapsayıcıdan tüm filmlerin/posterlerin çekimi (<li> elemanları)
        filmDetails = filmDetailsList.find_all("li")
        #> Filmleri ekrana ve dosyaya yazdırma işlemleri
        currentPageMoviesData = []
        for currentFilmDetail in filmDetails:
            movieHeadlineElement = currentFilmDetail.find('h2', attrs={'class': 'headline-2 prettify'}) # Film ismini ve yılını içeren kapsayıcının çekimi
            movieLinkElement = movieHeadlineElement.find('a')
            movieName = movieLinkElement.text # Link elementiden film isminin çekimi
            movieLink = SITE_DOMAIN + movieLinkElement.get('href') # SITE_DOMAIN + Link elementinden film adresinin çekimi https://letterboxd.com + /film/white-zombie/
            #> Kapsayıcıdan film yılının çekimi vw boş olma ihtimaline(olasılık mevcut) karşın önlemin alınması.
            try: movieYear = movieHeadlineElement.find('small').text
            except: movieYear = ''
            if CMD_PRINT_FILMS: print(f"{tempLoopCount}: {movieYear:4}, {movieName}, {movieLink}") # Kullanıcı eğer isterse çekilen filmler ekrana da yansıtılır.
            currentMovieData = [movieYear, movieName, movieLink]
            currentPageMoviesData.append(currentMovieData)
            tempLoopCount += 1
        writer.writerows(currentPageMoviesData) # Çekilen verinin toplu yazılma işlemi veya bu işlem tek tek yazma for içerisinde için writer.writerow(currentMovieData) ile kullanılabilir.
        return tempLoopCount # Mevcut film sırasına ait sayı geri döndürülür.
    except Exception as e:
        errorLine(e)  
        #txtLog('An error was encountered while obtaining movie information.', logFilePath)