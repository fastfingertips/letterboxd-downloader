from bs4 import BeautifulSoup
from constants.project import PRE_LOG_INFO, PRE_LOG_ERR
from utils.log.custom import errorLine, txtLog
from utils.request.base import fetch_page_dom

def fetch_page_dom_with_logging(url: str, timeout: int = 30) -> BeautifulSoup:
    """
    Retrieves the DOM structure of the specified page URL using BeautifulSoup, with logging.

    Args:
        url (str): The URL of the page to be retrieved.
        timeout (int): The timeout period for the request in seconds.

    Returns:
        BeautifulSoup: The parsed DOM structure of the page.
    """
    try:
        txtLog(f'{PRE_LOG_INFO}Attempting to connect to [{url}]')
        
        while True:
            try:
                dom = fetch_page_dom(url, timeout)  # Use the general fetch function
                
                if dom:
                    return dom  # Returns the page DOM
                
            except Exception as e:
                txtLog(f'{PRE_LOG_ERR}Error occurred while processing [{url}]')
                errorLine(e)
                continue

    except Exception as e:
        errorLine(e)
        txtLog(f'{PRE_LOG_ERR}Failed to connect to [{url}]')

    return None  # Return None if the process is interrupted or an error occurs
