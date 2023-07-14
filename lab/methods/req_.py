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

def getMetaContent(_dom, _obj):
    """
    a function that returns the content of the meta tag..
    """
    try:
        #> get the content of the meta tag.
        metaContent = _dom.find('meta', property=_obj).attrs['content']
    except AttributeError:
        #> if the meta tag is not found, return an empty string.
        print(f"{preCmdErr}Cannot retrieve '{_obj}' from the meta tag.")
        txtLog(f"Cannot retrieve '{_obj}' from the meta tag. Error Message: {AttributeError}")
        metaContent = ''
    return metaContent

def urlFix(_urlListItem, _urlList):
    #> get the DOM element of the page.
    urlListItemDom = doReadPage(_urlListItem)
    #> check the availability of the list and get the approved URL.
    userListAvailable, approvedListUrl = userListCheck(urlListItemDom, _urlListItem)
    #> if the list is available and the approved URL is not already in the URL list...
    if userListAvailable and approvedListUrl not in _urlList:
        #> add the approved URL to the URL list for further processing.
        _urlList.append(approvedListUrl)
    return _urlList

def userListCheck(_urlListItemDom, _urlListItem):
    """
    check if the user has a list in the given format. if not, prompt again.
    """
    try: # try to extract data from the meta tag; if not found, it's not a list.
        metaOgType = getMetaContent(_urlListItemDom,'og:type') 

        #> check if the meta tag indicates that it's a list.
        if metaOgType == "letterboxd:list":
            txtLog(f'{PRE_LOG_INFO}Meta content confirmed that the entered address is a list. Meta content: {metaOgType}')

            #> get the URL of the list from the meta tag.
            #> if the URL is not the same as the one entered, it means that the list has been redirected.
            metaOgUrl = getMetaContent(_urlListItemDom,'og:url')
            #> get the title of the list from the meta tag. Example: 'Search results for best comedy'
            metaOgTitle = getMetaContent(_urlListItemDom, 'og:title')
            #> get the username of the list owner from the body tag.
            bodyDataOwner = getBodyContent(_urlListItemDom,'data-owner')

            #> print the list owner's username and the list title.
            print(f'{preCmdCheck}{ced("Found it: ", color="green")}@{ced(bodyDataOwner,"yellow")} "{ced(metaOgTitle,"yellow")}"')

            #> if the entered URL matches the meta URL...
            if _urlListItem == metaOgUrl or f'{_urlListItem}/' == metaOgUrl:
                txtLog(f'{PRE_LOG_INFO}The list URL does not contain any redirects.')
            else: # Girilen URL Meta ile uyuşmuyorsa..
                print(f'{preCmdInfo}The list URL you entered contains redirects.')
                print(f'{preBlankCount}The list title was likely changed recently or you entered it incorrectly.')
                print(f'{preBlankCount}({ced("+", "red")}): {ced(_urlListItem, color="yellow")}')
                
                if _urlListItem in metaOgUrl:
                    msgInputUrl = ced(_urlListItem, color="yellow")
                    msgMetaOgUrlChange = ced(metaOgUrl.replace(_urlListItem,""), color="green")
                else:
                    metaLoop = len(metaOgUrl)
                    msgInputUrl = ''
                    msgMetaOgUrlChange = getChanges(metaLoop,_urlListItem,metaOgUrl)

                print(f'{preBlankCount}({ced("+", "green")}): {msgInputUrl}{msgMetaOgUrlChange} as the corrected URL.')
            txtLog(f'{PRE_LOG_INFO}List "{metaOgTitle}" found for {_urlListItem}')

            currentListAvaliable = True
    except Exception as e:
        errorLine(e)
        metaOgUrl = ''
        currentListAvaliable = False
    finally:
        return currentListAvaliable, metaOgUrl

def getListSignature(_listDict): # get list's signature
    #> extract the DOM element and detail page of the list
    listDom = _listDict['list_dom']
    listDetailPage = _listDict['list_detail_page']

    #> get the name of the list owner.
    listBy = listDom.select("[itemprop=name]")[0].text 

    #> get the title of the list.
    try:
        listTitle = listDom.select("[itemprop=title]")[0].text.strip()
    except IndexError:
        #> get the title of the list from the meta tag if it's not found in the DOM.
        listTitle = getMetaContent(listDom, 'og:title')

    #> get the creation date of the list.
    listPublicationTime = listDom.select(".published time")[0].text

    #> convert the creation date to a human-readable format.
    listPublicationTimeHumanize = arrow.get(listPublicationTime).humanize()

    #> get the number of pages in the list.
    listLastPage = getListLastPageNo(listDom, listDetailPage)

    #> calculate the number of movies in the list.
    listMovieCount =  getMovieCount(listLastPage, listDom, listDetailPage)

    try: ## try to extract filter information from the list page.
        #> get the year range filter information from the list page.
        domSelectedDecadeYear = listDom.select(".smenu-subselected")[3].text + 'movies only was done by.' 
        #> get the genre filter information from the list page.
        domSelectedGenre = listDom.select(".smenu-subselected")[2].text + 'only movies.'
        #> get the sorting filter information from the list page.
        domSelectedSortBy = listDom.select(".smenu-subselected")[0].text + '.'
    except Exception as e: ## if there is an error while extracting filter information...
        txtLog(f'{PRE_LOG_ERR}A problem occurred while retrieving filter information.')
        print('A problem occurred while retrieving filter information.')
        #> set each filter to 'Unknown' if the filter information cannot be obtained.
        domSelectedDecadeYear, domSelectedGenre, domSelectedSortBy = 3*'Unknown'

    try: ## get the update time of the list
        listUpdateTime = listDom.select(".updated time")[0].text
        #> convert the update time to a human-readable format.
        listUT = arrow.get(listUpdateTime).humanize()
    except Exception as e: ## if the update time cannot be obtained...
        errorLine(e)
        #> assume that the list has not been edited in case of an error.
        listUT = 'No editing.'

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