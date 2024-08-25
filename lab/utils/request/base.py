import requests
from bs4 import BeautifulSoup

def fetch_page_dom(url: str, timeout: int = 30) -> BeautifulSoup:
    """
    Retrieves the DOM structure of the specified page URL using BeautifulSoup.

    Args:
        url (str): The URL of the page to be retrieved.
        timeout (int): The timeout period for the request in seconds.

    Returns:
        BeautifulSoup: The parsed DOM structure of the page.
    """
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raises an exception for HTTP errors
        dom = BeautifulSoup(response.content.decode('utf-8'), 'html.parser')

        if dom:
            return dom  # Returns the page DOM

    except requests.ConnectionError as e:
        print("Connection Error: Please check your Internet connection.")
        print(f"Details: {e}")

    except requests.Timeout as e:
        print("Timeout Error: The request timed out.")
        print(f"Details: {e}")

    except requests.RequestException as e:
        print("Request Error: A general error occurred during the request.")
        print(f"Details: {e}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return None  # Return None if an error occurs
