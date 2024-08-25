from bs4 import BeautifulSoup
import requests

from constants.project import(
  PRE_LOG_INFO,
  PRE_LOG_ERR
)

from methods.log_ import(
  errorLine,
  txtLog
)

def fetch_page_dom(url: str) -> BeautifulSoup:
    """
    Retrieves the DOM structure of the specified page URL using BeautifulSoup.

    Args:
        url (str): The URL of the page to be retrieved.

    Returns:
        BeautifulSoup: The parsed DOM structure of the page.

    The function attempts to connect to the specified URL and parse its content into a BeautifulSoup object.
    It handles various exceptions related to network issues, such as connection errors, timeouts, and general request exceptions.
    If successful, it returns the DOM structure; otherwise, it logs the error and retries.
    """
    try:
        txtLog(f'{PRE_LOG_INFO}Attempting to connect to [{url}]')
        
        while True:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()  # Raises an exception for HTTP errors
                dom = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')
                
                if dom:
                    return dom  # Returns the page DOM
                
            except requests.ConnectionError as e:
                print("Connection Error: Please check your Internet connection.")
                print(f"Details: {e}")
                continue
                
            except requests.Timeout as e:
                print("Timeout Error: The request timed out.")
                print(f"Details: {e}")
                continue
                
            except requests.RequestException as e:
                print("Request Error: A general error occurred during the request.")
                print(f"Details: {e}")
                continue
                
            except KeyboardInterrupt:
                print("Process interrupted by the user.")
                break
                
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break
    
    except Exception as e:
        errorLine(e)
        txtLog(f'{PRE_LOG_ERR}Failed to connect to [{url}]')

    return None  # Return None if the process is interrupted or an error occurs