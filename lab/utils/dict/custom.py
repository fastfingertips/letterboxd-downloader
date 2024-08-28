import logging
import arrow

from utils.terminal import set_terminal_title

from utils.log.custom import log_error_with_line
from utils.color.custom import colored, blink_text
from utils.dom.custom import getMovieCount, get_meta_content, get_list_last_page_no

from constants.project import PRE_LOG_ERR, PRE_LOG_INFO, SUP_LINE
from constants.terminal import ICON_INFO, ICON_MIDDLE_DOT, ICON_MIDDLE_DOT_LIST


def get_list_signature(_listDict) -> dict:
    """
    a function that returns the signature of the list.
    """
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
        listTitle = get_meta_content(listDom, 'og:title')

    #> get the creation date of the list.
    listPublicationTime = listDom.select(".published time")[0].text

    #> convert the creation date to a human-readable format.
    listPublicationTimeHumanize = arrow.get(listPublicationTime).humanize()

    #> get the number of pages in the list.
    listLastPage = get_list_last_page_no(listDom, listDetailPage)

    #> calculate the number of movies in the list.
    listMovieCount = getMovieCount(listLastPage, listDom, listDetailPage)

    try: ## try to extract filter information from the list page.
        #> get the year range filter information from the list page.
        domSelectedDecadeYear = listDom.select(".smenu-subselected")[3].text + 'movies only was done by.' 
        #> get the genre filter information from the list page.
        domSelectedGenre = listDom.select(".smenu-subselected")[2].text + 'only movies.'
        #> get the sorting filter information from the list page.
        domSelectedSortBy = listDom.select(".smenu-subselected")[0].text + '.'
    except Exception as e: ## if there is an error while extracting filter information...
        logging.error(f'A problem occurred while retrieving filter information. {e}')
        #> set each filter to 'Unknown' if the filter information cannot be obtained.
        domSelectedDecadeYear, domSelectedGenre, domSelectedSortBy = 'Unknown', 'Unknown', 'Unknown'

    try: ## get the update time of the list
        listUpdateTime = listDom.select(".updated time")[0].text
        #> convert the update time to a human-readable format.
        listUT = arrow.get(listUpdateTime).humanize()
    except Exception as e: ## if the update time cannot be obtained...
        log_error_with_line(e)
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

    print(listSign)

    return listSign

def listSignature(_listDict) -> None:
    """
    Print the list information on the screen.
    """
    try:
        #> attempt to get list information from the list page.
        listSign = get_list_signature(_listDict)

        set_terminal_title(f"{_listDict['process_state']} Process: @{_listDict['list_owner']}.")

        signList = [
            f"\n{ICON_INFO}Process State: {blink_text(_listDict['process_state'],'green')}",
            SUP_LINE,
            f"{ICON_INFO}{colored('List info;', color='yellow')}",
            f"{ICON_MIDDLE_DOT}List by {colored(listSign['list_by'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Updated: {colored(listSign['list_update_time_humanize'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Published: {colored(listSign['list_publication_time_humanize'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}List title: {colored(listSign['list_title'], 'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Filters;",
            f"{ICON_MIDDLE_DOT_LIST}Filtered as {colored(listSign['list_selected_decade_year'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Filtered as {colored(listSign['list_selected_genre'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Movies sorted by {colored(listSign['list_selected_sort_by'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}List hash: {colored(_listDict['list_run_time'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Sayfa sayısı: {colored(listSign['list_last_page'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Number of movies: {colored(listSign['list_movie_count'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}List domain name: {colored(_listDict['list_domain_name'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}List URL: {colored(_listDict['list_url'],'blue', attrs=['bold'])}",
            f"{ICON_MIDDLE_DOT}Process URL: {colored(_listDict['list_detail_url'],'blue', attrs=['bold'])}"
        ]

        print('\n'.join(signList))
        logging.info("List's signature print success.")
    except Exception as e:
        log_error_with_line(e)
        logging.error("List signature print error.")