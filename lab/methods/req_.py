from bs4 import BeautifulSoup
import requests
import arrow

# -- Local Imports -- #

from .system_ import terminalTitle
from .hash_ import getChanges

from constants.project import(
    CMD_PRINT_FILMS,
    PRE_LOG_INFO,
    PRE_LOG_ERR,
    SITE_DOMAIN,
    SUP_LINE
)

from .color_ import(
    preCmdMiddleDotList,
    preCmdMiddleDot,
    preBlankCount,
    preCmdCheck,
    preCmdInfo,
    preCmdErr,
    cmdBlink,
    ced
)

from .log_ import(
    errorLine,
    txtLog
)

def getBodyContent(dom, obj):
    return dom.find('body').attrs[obj]

def getMetaContent(dom, obj): 
    try: metaContent = dom.find('meta', property=obj).attrs['content']
    except AttributeError:
        print(f"{preCmdErr}Meta etiketinden '{obj}' alınamadı.")
        txtLog(f"Meta etiketinden '{obj}' alınamadı. Hata Mesajı: {AttributeError}")
        metaContent = ''
    return metaContent

def urlFix(x, urlList, urlListItem):
    urlListItemDom = doReadPage(x) #: Sayfa dom'u alınır.
    userListAvailable, approvedListUrl = userListCheck(urlListItemDom, urlListItem) #: Liste kullanılabilirliği ve Doğrulanmış URL adresi elde edilir.
    if userListAvailable and approvedListUrl not in urlList: ## Liste kullanıma uygunsa ve doğrulanmış URL daha önce URL Listesine eklenmediyse..
        urlList.append(approvedListUrl) #: Doğrulanmış URL, işlem görecek URL Listesine ekleniyor.
    return urlList

def userListCheck(_url_list_item_dom, urlListItem): #: Kullanıcının girilen şekilde bir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
    try:
        try: #: meta etiketinden veri almayı dener eğer yoksa liste değil.
            metaOgType = getMetaContent(_url_list_item_dom,'og:type') 

            if metaOgType == "letterboxd:list": # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşılır.
                txtLog(f'{PRE_LOG_INFO}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {metaOgType}')
                metaOgUrl = getMetaContent(_url_list_item_dom,'og:url') #: Liste yönlendirmesi var mı bakıyoruz
                metaOgTitle = getMetaContent(_url_list_item_dom, 'og:title')  #: Liste ismini alıyoruz. Örnek: 'Search results for best comedy'
                bodyDataOwner = getBodyContent(_url_list_item_dom,'data-owner') #: Liste sahibinin kullanıcı ismi.
                print(f'{preCmdCheck}{ced("Found it: ", color="green")}@{ced(bodyDataOwner,"yellow")} "{ced(metaOgTitle,"yellow")}"') #: Liste sahibinin kullanıcı ismi ve liste ismi ekrana yazdırılır.

                #> Girilen URL Meta ile aynıysa..
                if urlListItem == metaOgUrl or f'{urlListItem}/' == metaOgUrl: txtLog(f'{PRE_LOG_INFO}Liste adresi yönlendirme içermiyor.')
                else: # Girilen URL Meta ile uyuşmuyorsa..
                    print(f'{preCmdInfo}Girdiğiniz liste linki yönlendirme içeriyor.')
                    print(f'{preBlankCount}Muhtemelen liste ismi yakın bir zamanda değişildi veya hatalı girdiniz.')
                    print(f'{preBlankCount}({ced("+","red")}): {ced(urlListItem, color="yellow")} adresini')
                    
                    if urlListItem in metaOgUrl:
                        msgInputUrl = ced(urlListItem, color="yellow")
                        msgMetaOgUrlChange = ced(metaOgUrl.replace(urlListItem,""), color="green")
                    else:
                        metaLoop = len(metaOgUrl)
                        msgInputUrl = ''
                        msgMetaOgUrlChange = getChanges(metaLoop,urlListItem,metaOgUrl)

                    print(f'{preBlankCount}({ced("+","green")}): {msgInputUrl}{msgMetaOgUrlChange} şeklinde değiştirdik.')
                txtLog(f'{PRE_LOG_INFO}{urlListItem} listesi bulundu: {metaOgTitle}')

                currentListAvaliable = True
        except Exception as e:
            errorLine(e)
            metaOgUrl = ''
            currentListAvaliable = False
    except Exception as e:
        errorLine(e)
        currentListAvaliable = False
    finally: return currentListAvaliable, metaOgUrl

def getListSignature(_listDict): # Get list's signature
    listDom = _listDict['list_dom']
    listDetailPage = _listDict['list_detail_page']

    listBy = listDom.select("[itemprop=name]")[0].text #: Liste sahibi ismi çekiliyor.
    try: listTitle = listDom.select("[itemprop=title]")[0].text.strip() #: Liste başlığının ismini çekiliyor.
    except IndexError: listTitle = getMetaContent(listDom, 'og:title') #: Liste başlığının ismini çekiliyor.
    listPublicationTime = listDom.select(".published time")[0].text #: Liste oluşturulma tarihi çekiliyor.
    listPublicationTimeHumanize = arrow.get(listPublicationTime).humanize()
    listLastPage = getListLastPageNo(listDom, listDetailPage) #: Liste sayfa sayısı çekiliyor.
    listMovieCount =  getMovieCount(listLastPage, listDom, listDetailPage) #: Listedeki film sayısı hesaplanıyor.

    try: ## Filtre bilgilerini liste sayfasından edinmeyi denemek.
        domSelectedDecadeYear = listDom.select(".smenu-subselected")[3].text + 'movies only was done by.' #: Liste sayfasından yıl aralık filtre bilgisi alınıyor.
        domSelectedGenre = listDom.select(".smenu-subselected")[2].text + 'only movies.' #: Liste sayfasından tür filtre bilgisi alınıyor.
        domSelectedSortBy = listDom.select(".smenu-subselected")[0].text + '.' #: Liste sayfasından sıralama filtre bilgisi alınıyor.
    except Exception as e: ## Filtre bilgileri edinirken bir hata oluşursa..
        txtLog(f'{PRE_LOG_ERR}Filtre bilgileri elde bir sorun gerçekleşti.')
        print('Filtre bilgileri elde bir sorun gerçekleşti.')
        domSelectedDecadeYear, domSelectedGenre, domSelectedSortBy = 3*'Unknown' #: Filtre bilgileri edinemediğinde her filtreye None eklenir.

    try: ## Search list update time
        listUpdateTime = listDom.select(".updated time")[0].text #: Liste düzenlenme vakti çekiliyor.
        listUT = arrow.get(listUpdateTime).humanize() #: Çekilen liste düzenlenme vakti okunmaya uygun hale getiriliyor.
    except Exception as e: #: Düzenleme vakti edinemezse.
        errorLine(e)
        listUT = 'No editing.' #: Hata alınırsa liste düzenlenmemiş varsayılır.

    listSign = {
        'list_by': listBy,
        'list_title': listTitle,
        'list_publication_time': listPublicationTime,
        'list_publication_time_humanize': listPublicationTimeHumanize,
        'list_last_page': listLastPage,
        'list_movie_count': listMovieCount,
        'list_update_time': listUpdateTime,
        'list_update_time_humanize': listUT,
        'list_selected_decade_year': domSelectedDecadeYear,
        'list_selected_genre': domSelectedGenre,
        'list_selected_sort_by': domSelectedSortBy
    }

    return listSign

def listSignature(_listDict): # print list's signature
    try:
        #> attempt to get list information from the list page.
        listSign = getListSignature(_listDict)

        terminalTitle(f"{_listDict['process_state']} Process: @{_listDict['list_owner']}.")

        signList = [
            f"\n{preCmdInfo}Process State: {cmdBlink(_listDict['process_state'],'green')}",
            SUP_LINE,
            f"{preCmdInfo}{ced('List info;', color='yellow')}",
            f"{preCmdMiddleDot}List by {ced(listSign['list_by'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}Updated: {ced(listSign['list_update_time_humanize'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}Published: {ced(listSign['list_publication_time_humanize'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}List title: {ced(listSign['list_title'], 'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}Filters;",
            f"{preCmdMiddleDotList}Filtered as {ced(listSign['list_selected_decade_year'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDotList}Filtered as {ced(listSign['list_selected_genre'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDotList}Movies sorted by {ced(listSign['list_selected_sort_by'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}List hash: {ced(_listDict['list_run_time'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}Sayfa sayısı: {ced(listSign['list_last_page'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}Number of movies: {ced(listSign['list_movie_count'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}List domain name: {ced(_listDict['list_domain_name'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}List URL: {ced(_listDict['list_url'],'blue', attrs=['bold'])}",
            f"{preCmdMiddleDot}Process URL: {ced(_listDict['list_detail_url'],'blue', attrs=['bold'])}"
        ]

        print('\n'.join(signList))
        txtLog(f"{PRE_LOG_INFO}List's signature print success.")
    except Exception as e:
        errorLine(e)
        txtLog(f'{PRE_LOG_ERR}List signature print error.')

def getMovieCount(_lastPageNo, _currentListDom, _currentUrlListItemDetailPage): # get list film count
    try:
        txtLog(f'{preCmdInfo}Getting the number of movies on the list meta description.')
        # Instead of connecting to the last page and getting the number of movies on the last page, which generates a GET request
        # and slows down the program, an alternative approach is used by getting the meta description of the list page.
        metaDescription = _currentListDom.find('meta', attrs={'name':'description'}).attrs['content']
        metaDescription = metaDescription[10:] # after 'A list of' in the description

        for i in range(6):
            try:
                int(metaDescription[i])
                ii = i+1
            except: pass
        movieCount = metaDescription[:ii]
        return movieCount
    except: # list's last page process
        txtLog(f'{preCmdInfo}Getting the number of movies on the list last page.')
        try:
            lastPageDom = doReadPage(f'{_currentUrlListItemDetailPage}{_lastPageNo}') # Getting lastpage dom.
            #> pulled page codes.
            lastPageArticles = lastPageDom.find('ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
            lastPageMoviesCount =  len(lastPageArticles) # film count.
            movieCount = ((int(_lastPageNo)-1)*100)+lastPageMoviesCount # total movie count.
            #> after the number of movies is found, it is written to the log file.
            txtLog(f"{PRE_LOG_INFO}Found list movie count as {movieCount}.")
            return movieCount # return movie count
        except Exception as e: # in case of possible error. (While getting dom)
            errorLine(e)
            txtLog(f'{PRE_LOG_ERR}An error occurred while obtaining the number of movies on the list last page.')

def getListLastPageNo(_currentListDom, _currentUrListItemDetailPage): # get list last page no
    try:
        # Note: To find the number of pages, count the li's. Take the last number.
        # The text of the link in the last 'li' will give us how many pages our list is.
        txtLog(f'{PRE_LOG_INFO}Checking the number of pages in the list..')

        #> not created link when the number of movies is 100 or less in the list.
        lastPageNo = _currentListDom.find('div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text 
        txtLog(f'{PRE_LOG_INFO}The list has more than one page ({lastPageNo}).')
        getMovieCount(lastPageNo, _currentListDom, _currentUrListItemDetailPage)
    except AttributeError: # exception when there is only one page.
        txtLog(f'{PRE_LOG_INFO}There is no more than one page, this list is one page.')
        lastPageNo = 1 # when the number of pages cannot be obtained, the number of pages is marked as 1.
        getMovieCount(lastPageNo, _currentListDom, _currentUrListItemDetailPage) # send page info.
    except Exception as e:
        errorLine(e)
    finally:
        txtLog(f'{PRE_LOG_INFO}Communication with the page is complete. It is learned that the number of pages in the list is {lastPageNo}.')
        return lastPageNo

def doReadPage(_url):
    #> Reads and retrieves the DOM of the specified page URL.
    try:
        #> Provides information in the log file at the beginning of the connection.
        txtLog(f'{PRE_LOG_INFO}Trying to connect to [{_url}]') 
        while True:
            #> https://stackoverflow.com/questions/23013220/max-retries-exceeded-with-url-in-requests
            try:
                urlResponseCode = requests.get(_url, timeout=30)
                urlDom = BeautifulSoup(urlResponseCode.content.decode('utf-8'), 'html.parser')
                if urlDom != None:
                    return urlDom # Returns the page DOM
            except requests.ConnectionError as e:
                print("OOPS!! Connection Error. Make sure you are connected to the Internet. Technical details are provided below.")
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
            except KeyboardInterrupt:
                print("Someone closed the program")
            except Exception as e:
                print('Error:', e)
    except Exception as e:
        #> If an error occurs while obtaining the DOM...
        errorLine(e)
        txtLog(f'{PRE_LOG_ERR}Connection to the address failed [{_url}]')

def doPullFilms(_loopCount, _currentDom, _writer): # gettin' films and write to csv
    try:
        #> getting' films/posters container (<ul> element)
        filmDetailsList = _currentDom.find('ul', attrs={'class': 'js-list-entries poster-list -p70 film-list clear film-details-list'})

        #> above line is tryin' to get container, if it's None, tryin' alternative ways to get it
        for currentAlternative in ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']:
            if filmDetailsList is None: filmDetailsList = _currentDom.select_one(currentAlternative)
            else:
                print(f'{preCmdInfo}{_loopCount} and after film/poster container pulled without alternative help.')
                break
        else:
            if filmDetailsList is None:
                print(f'{preCmdInfo}{_loopCount} and after film/poster container could not be pulled.')
            else:
                print(f'{preCmdInfo}{_loopCount} and after film/poster container pulled with alternative help.')

        #> getting' container's all films/posters (<li> elements)
        filmDetails = filmDetailsList.find_all("li")

        #> printing and writing films to file operations
        currentPageMoviesData = []
        for currentFilmDetail in filmDetails:
            #> pulling container of movie name and year
            movieHeadlineElement = currentFilmDetail.find('h2', attrs={'class': 'headline-2 prettify'}) 
            movieLinkElement = movieHeadlineElement.find('a')
            movieName = movieLinkElement.text # Pulling movie name from link element

            #> pulling movie link from link element https://letterboxd.com(SITE_DOMAIN) + /film/white-zombie/
            movieLink = SITE_DOMAIN + movieLinkElement.get('href') 

            #> pulling and checking the movie year from the container and taking precautions against the possibility of being empty
            try:
                movieYear = movieHeadlineElement.find('small').text
            except:
                movieYear = ''
                txtLog(f'{PRE_LOG_ERR}Movie year could not be pulled. Link: {movieLink}')

            if CMD_PRINT_FILMS: # if user want to print films to console, this line will check it
                print(f"{_loopCount}: {movieYear:4}, {movieName}, {movieLink}")

            currentMovieData = [movieYear, movieName, movieLink] # 1973, World on a Wire, https://letterboxd.com/film/world-on-a-wire/
            currentPageMoviesData.append(currentMovieData)
            _loopCount += 1

        #> Pulled data is written to the file.
        #> if you want to write the data one by one, you can use writer.writerow(currentMovieData) in for.
        _writer.writerows(currentPageMoviesData)

        return _loopCount # the number of movies belonging to the current page is returned.
    except Exception as e:
        errorLine(e)
        txtLog('An error was encountered while obtaining movie information.')