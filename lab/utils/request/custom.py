import logging
from bs4 import BeautifulSoup
from utils.log.custom import log_error_with_line
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
        logging.info(f'Attempting to retrieve DOM from URL: {url}')
        while True:
            try:
                dom = fetch_page_dom(url, timeout)
                if dom:
                    logging.info(f'Successfully retrieved DOM from {url}.')
                    return dom
            except Exception as e:
                logging.error(f'Error occurred while processing URL: {url}')
                log_error_with_line(e)
                continue
    except Exception as e:
        logging.error(f'Error occurred while fetching DOM from URL: {url}')
        log_error_with_line(e)

    return None
