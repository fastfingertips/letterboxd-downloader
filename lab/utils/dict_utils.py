import arrow
from constants.project import PRE_LOG_ERR
from methods.req_ import getMovieCount
from methods.log_ import txtLog, errorLine
from utils.dom_utils import (
  get_meta_content,
  get_list_last_page_no
)

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