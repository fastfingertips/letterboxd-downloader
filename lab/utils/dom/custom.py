import csv
from bs4 import BeautifulSoup
from utils.request import fetch_page_dom
from utils.log.custom import txtLog, errorLine

from constants.project import PRE_LOG_ERR, PRE_LOG_INFO, SITE_DOMAIN, CMD_PRINT_FILMS
from constants.terminal import PRE_CMD_INFO


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

def extract_and_write_films(loop_count: int, current_dom: BeautifulSoup, writer: csv.writer) -> int:
    """
    Extracts film information from the given BeautifulSoup DOM and writes it to a CSV file.
    
    Args:
        loop_count (int): The current iteration count for logging.
        current_dom (BeautifulSoup): The BeautifulSoup object representing the page's DOM.
        writer (csv.writer): CSV writer object used to write data to a CSV file.
        
    Returns:
        int: The updated loop count after processing the films.
        
    Raises:
        Exception: If an error occurs while retrieving film information.
    """
    try:
        # Attempt to locate the films/posters container (<ul> element) using primary selector.
        film_details_list = current_dom.find('ul', attrs={'class': 'js-list-entries poster-list -p70 film-list clear film-details-list'})

        # Try alternative selectors if primary selector fails.
        if film_details_list:
            # Primary selector succeeded.
            txtLog(f'{PRE_CMD_INFO}{loop_count}: Film/poster container found using primary selector.')
        else:
            # Primary selector failed, try alternative selectors.
            for alternative_selector in ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']:
                film_details_list = current_dom.select_one(alternative_selector)
                if film_details_list:
                    # Alternative selector succeeded.
                    txtLog(f'{PRE_CMD_INFO}{loop_count}: Film/poster container found using alternative selector: {alternative_selector}')
                    break
            else:
                # All selectors failed.
                txtLog(f'{PRE_CMD_INFO}{loop_count}: Film/poster container could not be found using any selector.')
                raise Exception('Film/poster container could not be found using any selector.')

        # Extract film details (<li> elements) from the container.
        film_details = film_details_list.find_all("li")

        # Prepare a list to store current page's movie data.
        current_page_movies_data = []
        for film_detail in film_details:
            # Extract movie name and link.
            movie_headline_element = film_detail.find('h2', attrs={'class': 'headline-2 prettify'}) 
            movie_link_element = movie_headline_element.find('a')
            # Pulling movie name from link element
            movie_name = movie_link_element.text

            # Pulling movie link from link element
            # https://letterboxd.com(SITE_DOMAIN) + /film/white-zombie/
            movie_link = SITE_DOMAIN + movie_link_element.get('href') 

            # Extract movie year, default to empty if not found.
            movie_year = ''
            year_element = movie_headline_element.find('small')
            if year_element:
                movie_year = year_element.text
            else:
                txtLog(f'{PRE_LOG_ERR}Movie year could not be retrieved. Link: {movie_link}')

            # Print film information if enabled.
            if CMD_PRINT_FILMS:
                print(f"{loop_count}: {movie_year:4}, {movie_name}, {movie_link}")

            # Append movie data to list
            # 1973, World on a Wire, https://letterboxd.com/film/world-on-a-wire/
            current_movie_data = [movie_year, movie_name, movie_link]
            current_page_movies_data.append(current_movie_data)
            loop_count += 1

        # Write collected movie data to the CSV file. If you want to write the data
        # ... one by one, you can use writer.writerow(current_movie_data) in for.
        writer.writerows(current_page_movies_data)

        # The number of movies belonging to the current page is returned.
        return loop_count
    except Exception as e:
        errorLine(e)
        txtLog('An error occurred while retrieving film information.')
        raise