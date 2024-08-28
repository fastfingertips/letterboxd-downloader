import csv

from bs4 import BeautifulSoup

from utils.request import fetch_page_dom

from utils.color.custom import colored
from utils.log.custom import txtLog, errorLine
from utils.text.custom import highlight_changes

from constants.project import PRE_LOG_ERR, PRE_LOG_INFO, SITE_DOMAIN, CMD_PRINT_FILMS
from constants.terminal import ICON_INFO, ICON_CHECK, PRE_BLANK_COUNT


def getMovieCount(_lastPageNo, _currentListDom, _currentUrlListItemDetailPage) -> int:
    """
    Get the number of movies on the list.
    """
    try:
        txtLog(f'{ICON_INFO}Getting the number of movies on the list meta description.')
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
        txtLog(f'{ICON_INFO}Getting the number of movies on the list last page.')
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
            txtLog(f'{ICON_INFO}{loop_count}: Film/poster container found using primary selector.')
        else:
            # Primary selector failed, try alternative selectors.
            for alternative_selector in ['ul.film-list', 'ul.poster-list', 'ul.film-details-list']:
                film_details_list = current_dom.select_one(alternative_selector)
                if film_details_list:
                    # Alternative selector succeeded.
                    txtLog(f'{ICON_INFO}{loop_count}: Film/poster container found using alternative selector: {alternative_selector}')
                    break
            else:
                # All selectors failed.
                txtLog(f'{ICON_INFO}{loop_count}: Film/poster container could not be found using any selector.')
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

def get_list_last_page_no(current_list_dom: BeautifulSoup, current_url_list_item_detail_page: str) -> int:
    """
    Retrieves the number of pages in the list by finding the last page number from the pagination.

    Args:
        current_list_dom (BeautifulSoup): The parsed DOM structure of the current list page.
        current_url_list_item_detail_page (str): The URL of the detail page for the current list item.

    Returns:
        int: The number of the last page in the list.
        
    If there is only one page or if an error occurs, the function defaults to returning 1.

    Logs the process and any errors encountered during the retrieval of the last page number.
    """
    try:
        txtLog(f'{PRE_LOG_INFO}Checking the number of pages in the list...')
        
        # Locate the pagination container and find the last page number
        pagination_div = current_list_dom.find('div', class_='paginate-pages')
        if not pagination_div:
            raise ValueError('Pagination container not found.')
        
        page_items = pagination_div.find_all('li')
        if not page_items:
            raise ValueError('No pagination items found.')
        
        last_page_number = page_items[-1].a.text.strip()
        last_page_number = int(last_page_number)  # Convert to integer
        
        txtLog(f'{PRE_LOG_INFO}The list has more than one page (Last page number: {last_page_number}).')
        
        # Process the movie count on the last page
        getMovieCount(last_page_number, current_list_dom, current_url_list_item_detail_page)
        
    except (AttributeError, ValueError) as e:
        txtLog(f'{PRE_LOG_INFO}Error determining the number of pages: {e}')
        last_page_number = 1  # Default to 1 if there is an error or single page
        
        # Handle the case with only one page
        getMovieCount(last_page_number, current_list_dom, current_url_list_item_detail_page)
        
    except Exception as e:
        errorLine(e)
        last_page_number = 1  # Default to 1 on unexpected exceptions
    
    finally:
        txtLog(f'{PRE_LOG_INFO}Completed page count check. Last page number is {last_page_number}.')
        return last_page_number
    
def get_body_content(dom: BeautifulSoup, attribute: str) -> str:
    """
    Retrieves the specified attribute value from the <body> tag of the given DOM.

    Args:
        dom (BeautifulSoup): The parsed DOM structure of a web page.
        attribute (str): The attribute whose value is to be retrieved from the <body> tag.

    Returns:
        str: The value of the specified attribute from the <body> tag.

    Raises:
        ValueError: If the <body> tag or the specified attribute is not found in the DOM.

    The function searches for the <body> tag in the provided DOM and attempts to retrieve the value of the specified attribute.
    If the attribute is not present or the <body> tag is missing, a ValueError is raised.
    """
    body_tag = dom.find('body')

    if body_tag is None:
        raise ValueError("The <body> tag was not found in the DOM.")

    if attribute not in body_tag.attrs:
        raise ValueError(f"The attribute '{attribute}' was not found in the <body> tag.")
    
    return body_tag.attrs[attribute]

def get_meta_content(dom: BeautifulSoup, property_name: str, attribute_name: str = 'content', raise_on_error: bool = True) -> str:
    """
    Retrieves the value of a specified attribute from a <meta> tag with a specified property attribute.

    Args:
        dom (BeautifulSoup): The parsed DOM structure of a web page.
        property_name (str): The property attribute value to search for in the <meta> tag.
        attribute_name (str): The name of the attribute whose value is to be retrieved from the <meta> tag. Defaults to 'content'.
        raise_on_error (bool): Whether to raise an exception if the <meta> tag or the specified attribute is not found. If False, returns an empty string instead.

    Returns:
        str: The value of the specified attribute from the <meta> tag, or an empty string if not found and raise_on_error is False.
        
    If raise_on_error is True and the <meta> tag or the specified attribute is missing, a ValueError is raised.
    Otherwise, an empty string is returned and the error is logged.

    Raises:
        ValueError: If the <meta> tag with the specified property attribute is not found and raise_on_error is True.
    """
    try:
        meta_tag = dom.find('meta', property=property_name)
        
        if meta_tag is None:
            if raise_on_error:
                raise ValueError(f"Meta tag with property '{property_name}' not found.")
            return ''
        
        if attribute_name not in meta_tag.attrs:
            if raise_on_error:
                raise ValueError(f"Attribute '{attribute_name}' not found in meta tag with property '{property_name}'.")
            return ''
        
        return meta_tag.attrs[attribute_name]
    
    except Exception as e:
        txtLog(f"Error retrieving '{attribute_name}' from the meta tag with property '{property_name}'. Error Message: {e}")
        if raise_on_error:
            raise
        return ''

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
            print(f'{ICON_CHECK}{colored("Found it: ", color="green")}@{colored(bodyDataOwner,"yellow")} "{colored(metaOgTitle,"yellow")}"')

            #> if the entered URL matches the meta URL...
            if _urlListItem == metaOgUrl or f'{_urlListItem}/' == metaOgUrl:
                txtLog(f'{PRE_LOG_INFO}The list URL does not contain any redirects.')
            else: # Girilen URL Meta ile uyuşmuyorsa..
                print(f'{ICON_INFO}The list URL you entered contains redirects.')
                print(f'{PRE_BLANK_COUNT}The list title was likely changed recently or you entered it incorrectly.')
                print(f'{PRE_BLANK_COUNT}({colored("+", "red")}): {colored(_urlListItem, color="yellow")}')
                
                if _urlListItem in metaOgUrl:
                    msgInputUrl = colored(_urlListItem, color="yellow")
                    msgMetaOgUrlChange = colored(metaOgUrl.replace(_urlListItem,""), color="green")
                else:
                    msgInputUrl = ''
                    msgMetaOgUrlChange = highlight_changes(_urlListItem, metaOgUrl)

                print(f'{PRE_BLANK_COUNT}({colored("+", "green")}): {msgInputUrl}{msgMetaOgUrlChange} as the corrected URL.')
            txtLog(f'{PRE_LOG_INFO}List "{metaOgTitle}" found for {_urlListItem}')

            currentListAvaliable = True
    except Exception as e:
        errorLine(e)
    finally:
        return currentListAvaliable, metaOgUrl