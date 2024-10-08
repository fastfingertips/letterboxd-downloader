from utils.request import fetch_page_dom
from utils.dom.custom import check_user_list


def fix_url(url_item: str, url_list: list) -> list:
    """
    Processes and validates a URL from the provided item, adding it to the list if it meets specified conditions.

    Args:
        url_item (str): The URL item to be processed.
        url_list (list): The list of URLs to be updated with the valid URL.

    Returns:
        list: The updated list of URLs with the new, validated URL if applicable.

    The function performs the following:
    1. Retrieves the DOM structure of the page from the given URL item.
    2. Checks if the user list is available in the DOM and retrieves the validated URL.
    3. Appends the validated URL to the url_list if it's not already present.
    """
    dom = fetch_page_dom(url_item)
    is_available, validated_url = check_user_list(dom, url_item)
    
    if is_available and validated_url not in url_list:
        url_list.append(validated_url)
    
    return url_list

def extract_list_domain_name(url: str) -> str:
    """
    Extracts the domain name or identifier from a given URL after the '/list/' segment.

    Args:
        url (str): The URL string to process.

    Returns:
        str: The extracted domain name or identifier. If '/list/' is not found, returns an empty string.
    """
    segment = '/list/'
    try:
        start_index = url.index(segment) + len(segment)
        return url[start_index:].replace('/', "")
    except ValueError:
        # If '/list/' is not found in the URL, return an empty string
        return ""