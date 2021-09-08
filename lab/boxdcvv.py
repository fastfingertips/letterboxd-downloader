import csv
from typing import Collection
from pandas import DataFrame
import requests
from bs4 import BeautifulSoup
from datetime import datetime

if True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    user_name = str(input("Username(Not display name): ")).lower()
    list_name = str(input("List_Name(Domain): ")).lower()
    # > Dosya çakışma sorunları için farklı isimler ürettik.
    zaman = datetime.now().strftime('%d%m%Y%H%M')
    csv_name = f"{user_name}-({zaman}).csv"


if True:
    # > Domain'in parçalanması
    prefix = "https://"
    main = "letterboxd.com"
    url = main + "/" + user_name + "/list/" + list_name
    domain_page = 1
    suffix = "/detail/page/" + str(domain_page)

    # > Domain'in doğru olup olmadığı kullanıcıya sorulur,
    # > doğruysa kullanıcı enter'a basar ve program verileri çeker.
    ent = input("Is the domain correct? (Enter): "+url + "\n: ").lower()
    if ent == "":
        # > Parçalanan Domain toplanarak, istek atıldı.
        page_url = requests.get(prefix + url + suffix)
        # > Sayfa kodları çekildi.
        soup = BeautifulSoup(
            page_url.content.decode('utf-8'), 'html.parser')
        # > Çekilen sayfa kodları, bir filtre uygulanarak daraltıldı.
        articles = soup.find('ul', attrs={
            'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")

        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        try:
            # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
            sayfa = soup.find(
                'div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text
            print(str(sayfa) + " sayfası olan bir listedir.")
            domain_page = sayfa
            # > Sayfa sayısını öğrenmek için bir ön hazırlık.
            last_page_url = requests.get(prefix + url + suffix)
            last_page_films = 1
            # > Son sayfadaki filmlerin sayısını öğrenip listedeki toplam film sayısını belirlemek.
            film_sayisi = ((sayfa-1)*100)+last_page_films
        except:
            # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
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
