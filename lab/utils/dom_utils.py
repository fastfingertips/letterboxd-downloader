from termcolor import colored as ced
from bs4 import BeautifulSoup

from utils.dom.custom import getMovieCount
from utils.log.custom import errorLine, txtLog

from utils.hash_utils import highlight_changes

from constants.terminal import PRE_CMD_CHECK, PRE_CMD_INFO, PRE_BLANK_COUNT
from constants.project import PRE_LOG_INFO


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
                    msgMetaOgUrlChange = highlight_changes(_urlListItem, metaOgUrl)

                print(f'{PRE_BLANK_COUNT}({ced("+", "green")}): {msgInputUrl}{msgMetaOgUrlChange} as the corrected URL.')
            txtLog(f'{PRE_LOG_INFO}List "{metaOgTitle}" found for {_urlListItem}')

            currentListAvaliable = True
    except Exception as e:
        errorLine(e)
    finally:
        return currentListAvaliable, metaOgUrl