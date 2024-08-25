from termcolor import colored as ced

# -- Local Imports -- #

from utils.terminal_utils import terminalTitle
from utils.hash_utils import getChanges
from utils.cmd_format import cmdBlink
from utils.request_utils import fetch_page_dom
from utils.dict_utils import get_list_signature
from utils.dom_utils import (
  get_body_content,
  get_meta_content
)

from constants.project import(
    CMD_PRINT_FILMS,
    PRE_LOG_INFO,
    PRE_LOG_ERR,
    SITE_DOMAIN,
    SUP_LINE
)

from constants.terminal import(
    PRE_CMD_MIDDLE_DOT_LIST,
    PRE_CMD_MIDDLE_DOT,
    PRE_BLANK_COUNT,
    PRE_CMD_CHECK,
    PRE_CMD_INFO
)

from .log_ import(
    errorLine,
    txtLog
)

 
def check_user_list(_urlListItemDom, _urlListItem) -> tuple:
    """
    checks the availability of the list and returns the approved URL.
    """
    metaOgUrl = ''
    currentListAvaliable = False
    try: # try to extract data from the meta tag; if not found, it's not a list.
        metaOgType = get_meta_content(_urlListItemDom,'og:type') 

        #> check if the meta tag indicates that it's a list.
        if metaOgType == "letterboxd:list":
            txtLog(f'{PRE_LOG_INFO}Meta content confirmed that the entered address is a list. Meta content: {metaOgType}')

            #> get the URL of the list from the meta tag.
            #> if the URL is not the same as the one entered, it means that the list has been redirected.
            metaOgUrl = get_meta_content(_urlListItemDom,'og:url')
            #> get the title of the list from the meta tag. Example: 'Search results for best comedy'
            metaOgTitle = get_meta_content(_urlListItemDom, 'og:title')
            #> get the username of the list owner from the body tag.
            bodyDataOwner = get_body_content(_urlListItemDom,'data-owner')

            #> print the list owner's username and the list title.
            print(f'{PRE_CMD_CHECK}{ced("Found it: ", color="green")}@{ced(bodyDataOwner,"yellow")} "{ced(metaOgTitle,"yellow")}"')

            #> if the entered URL matches the meta URL...
            if _urlListItem == metaOgUrl or f'{_urlListItem}/' == metaOgUrl:
                txtLog(f'{PRE_LOG_INFO}The list URL does not contain any redirects.')
            else: # Girilen URL Meta ile uyuşmuyorsa..
                print(f'{PRE_CMD_INFO}The list URL you entered contains redirects.')
                print(f'{PRE_BLANK_COUNT}The list title was likely changed recently or you entered it incorrectly.')
                print(f'{PRE_BLANK_COUNT}({ced("+", "red")}): {ced(_urlListItem, color="yellow")}')
                
                if _urlListItem in metaOgUrl:
                    msgInputUrl = ced(_urlListItem, color="yellow")
                    msgMetaOgUrlChange = ced(metaOgUrl.replace(_urlListItem,""), color="green")
                else:
                    msgInputUrl = ''
                    msgMetaOgUrlChange = getChanges(_urlListItem, metaOgUrl)

                print(f'{PRE_BLANK_COUNT}({ced("+", "green")}): {msgInputUrl}{msgMetaOgUrlChange} as the corrected URL.')
            txtLog(f'{PRE_LOG_INFO}List "{metaOgTitle}" found for {_urlListItem}')

            currentListAvaliable = True
    except Exception as e:
        errorLine(e)
    finally:
        return currentListAvaliable, metaOgUrl

def listSignature(_listDict) -> None:
    """
    Print the list information on the screen.
    """
    try:
        #> attempt to get list information from the list page.
        listSign = get_list_signature(_listDict)

        terminalTitle(f"{_listDict['process_state']} Process: @{_listDict['list_owner']}.")

        signList = [
            f"\n{PRE_CMD_INFO}Process State: {cmdBlink(_listDict['process_state'],'green')}",
            SUP_LINE,
            f"{PRE_CMD_INFO}{ced('List info;', color='yellow')}",
            f"{PRE_CMD_MIDDLE_DOT}List by {ced(listSign['list_by'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Updated: {ced(listSign['list_update_time_humanize'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Published: {ced(listSign['list_publication_time_humanize'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List title: {ced(listSign['list_title'], 'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Filters;",
            f"{PRE_CMD_MIDDLE_DOT_LIST}Filtered as {ced(listSign['list_selected_decade_year'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Filtered as {ced(listSign['list_selected_genre'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Movies sorted by {ced(listSign['list_selected_sort_by'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List hash: {ced(_listDict['list_run_time'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Sayfa sayısı: {ced(listSign['list_last_page'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Number of movies: {ced(listSign['list_movie_count'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List domain name: {ced(_listDict['list_domain_name'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}List URL: {ced(_listDict['list_url'],'blue', attrs=['bold'])}",
            f"{PRE_CMD_MIDDLE_DOT}Process URL: {ced(_listDict['list_detail_url'],'blue', attrs=['bold'])}"
        ]

        print('\n'.join(signList))
        txtLog(f"{PRE_LOG_INFO}List's signature print success.")
    except Exception as e:
        errorLine(e)
        txtLog(f'{PRE_LOG_ERR}List signature print error.')

def getMovieCount(_lastPageNo, _currentListDom, _currentUrlListItemDetailPage) -> int:
    """
    Get the number of movies on the list.
    """
    try:
        txtLog(f'{PRE_CMD_INFO}Getting the number of movies on the list meta description.')
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
        txtLog(f'{PRE_CMD_INFO}Getting the number of movies on the list last page.')
        try:
            lastPageDom = fetch_page_dom(f'{_currentUrlListItemDetailPage}{_lastPageNo}') # Getting lastpage dom.
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

def doPullFilms(_loopCount, _currentDom, _writer) -> None:
    """
    This function pulls the films on the list page and writes them to the csv file.
    """
    try:
        #> getting' films/posters container (<ul> element)
        filmDetailsList = _currentDom.find('ul', attrs={'class': 'js-list-entries poster-list -p70 film-list clear film-details-list'})

        #> above line is tryin' to get container, if it's None, tryin' alternative ways to get it
        for currentAlternative in ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']:
            if filmDetailsList is None: filmDetailsList = _currentDom.select_one(currentAlternative)
            else:
                print(f'{PRE_CMD_INFO}{_loopCount} and after film/poster container pulled without alternative help.')
                break
        else:
            if filmDetailsList is None:
                print(f'{PRE_CMD_INFO}{_loopCount} and after film/poster container could not be pulled.')
            else:
                print(f'{PRE_CMD_INFO}{_loopCount} and after film/poster container pulled with alternative help.')

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