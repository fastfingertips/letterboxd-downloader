from pandas import DataFrame
import requests
from bs4 import BeautifulSoup

_user = "crew"  # letterboxd profile
_list = "2021-oscars-all-nominated-films"
page = requests.get(f'https://letterboxd.com/{_user}/list/{_list}/detail')
soup = BeautifulSoup(page.content.decode('utf-8'), 'html.parser')
all_li = soup.find(
    'ul', attrs={'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
film_no = 1
for current_li in all_li:
    # Oda ismini çektik
    film = current_li.find(
        'h2', attrs={'class': 'headline-2 prettify'})
    film_name = film.find('a').text

    try:
        film_year = film.find('small').text
    except:
        film_year = "Blank"
    finally:
        print(f'{film_no}) {film_name} ({film_year})')
    film_no += 1
