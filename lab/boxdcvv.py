import csv
from typing import Collection
from pandas import DataFrame
import requests
from bs4 import BeautifulSoup

if True:
    user_name = str(input("Username(Not display name): ")).lower()
    list_name = str(input("List_Name(Domain): ")).lower()
    csv_name = input("CSV Name: ")+".csv"
    # Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    # Yani domaine uygun bir hale geitrdim.

    if True:
        main = "letterboxd.com/"
        url = main + user_name + "/list/" + list_name
        prefix = "https://"
        domain_page = 1
        suffix = "/detail/page/" + str(domain_page)
        ent = input("Is the domain correct? (Enter): "+url + "\n: ").lower()
        # Domain doğruysa kullanıcı enter'a basar ve program verileri çeker.

        if ent == "":
            page_url = requests.get(prefix + url + suffix)
            soup = BeautifulSoup(
                page_url.content.decode('utf-8'), 'html.parser')

            # Kaç sayfa olduğunuu öğreniyoruz.
            articles = soup.find('ul', attrs={
                                 'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")

            # paginate-pages Class'lı divin içindeki li'leri sayarak sayfa sayısını bulmuştuk fakat çöktü
            # çünkü tüm sayfaların bağlantısı ve bilgisi yoktu. bu nedenle son li'nin değerini alıyoruz sadece
            try:
                sayfa = soup.find(
                    'div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text
                print(str(sayfa) + " sayfası olan bir listedir.")
                domain_page = sayfa
                last_page_url = requests.get(prefix + url + suffix)

                last_page_films = 1
                film_sayisi = ((sayfa-1)*100)+last_page_films
            except:
                print("Sayfa sayısı yok, bu sayfa tek sayfadır.")

            # Csv dosyamızı açtık
            with open(csv_name, 'w', newline='', encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Sıra", "Filmİsmi", "YayınYılı"])
                # Filmleri çekiyoruz
                dongu_no = 1
                for room in articles:
                    # Oda ismini çektik
                    film = room.find(
                        'h2', attrs={'class': 'headline-2 prettify'})
                    film_adi = film.find('a').text
                    # Film yılı bazen boş olabiliyor. Önlem alıyoruz"
                    try:
                        film_yili = film.find('small').text
                    except:

                        film_yili = "Yok"
                    # Her seferinde Csv dosyasına çektiğimiz bilgileri yazıyoruz.
                    print(f'{dongu_no}) {film_adi} ({film_yili})')
                    writer.writerow(
                        [str(dongu_no), str(film_adi), str(film_yili)])
                    dongu_no += 1
                file.close()
print(f'{dongu_no-1} Film bulundu. Tüm filmler {csv_name +" dosyasına"} aktarıldı.')
