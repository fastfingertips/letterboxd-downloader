from bs4 import BeautifulSoup
from constants.project import PRE_LOG_INFO
from methods.req_ import getMovieCount
from methods.log_ import(
    errorLine,
    txtLog
)

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