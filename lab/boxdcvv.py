import csv
from typing import Collection
from pandas import DataFrame
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def readpage(r_url):
    page_url = requests.get(r_url)
    # > Sayfa kodları çekildi.
    soup = BeautifulSoup(page_url.content.decode('utf-8'), 'html.parser')
    return soup


def countrooms(r_article):
    data_count = 0
    for rooms in r_article:
        data_count += 1
    return data_count


def pullfilms(r_count, r_soup):
    # > Çekilen sayfa kodları, bir filtre uygulanarak daraltıldı.
    articles = r_soup.find('ul', attrs={
        'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
    dongu_no = r_count
    for rooms in articles:
        # Oda ismini çektik
        film = rooms.find(
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
    return dongu_no


if True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    user_name = str(input("Username(Not display name): ")).lower()
    list_name = str(input("List_Name(Domain): ")).lower()
    # > Dosya çakışma sorunları için farklı isimler ürettik.
    zaman = datetime.now().strftime('%d%m%Y%H%M')
    csv_name = f"{user_name}-({zaman}).csv"

if True:
    # > Domain'in parçalanması
    main_protocol = "https://"
    site_url = "letterboxd.com"
    domain = main_protocol + site_url
    mini_url = f'{domain}/{user_name}/list/{list_name}'
    url = f'{mini_url}/detail/page/'
    # > Domain'in doğru olup olmadığı kullanıcıya sorulur,
    # > doğruysa kullanıcı enter'a basar ve program verileri çeker.
    ent = input(
        f"Is the domain correct? (Enter): {mini_url}\n: ").lower()

    if ent == "":
        # > Parçalanan Domain toplanarak, istek atıldı.
        soup = readpage(mini_url)

        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        try:
            # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
            lastPage_No = soup.find(
                'div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text
            print(f"{lastPage_No} sayfası olan bir listedir.")
            pageNo = lastPage_No

            # > Son sayfaya bağlanmak için bir ön hazırlık.
            lastsoup = readpage(url + lastPage_No)
            # > Sayfa kodları çekildi.
            lastarticles = lastsoup.find('ul', attrs={
                'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
            lastpage_fcount = countrooms(lastarticles)
            # < Film sayısı öğrenildi.
            # > Toplam film sayısını belirlemek.
            film_sayisi = ((int(lastPage_No)-1)*100)+lastpage_fcount
            print(f"Bu listedeki film sayısı: {film_sayisi}")
        except:
            # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
            print("Sayfa sayısı yok, bu sayfa tek sayfadır.")

        # Csv dosyamızı açtık
        with open(csv_name, 'w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Sıra", "Filmİsmi", "YayınYılı"])
            # Filmleri çekiyoruz
            dongu_no = 1
            for x in range(int(lastPage_No)):
                print(f"Connecting to: {url}{str(x+1)}")
                current_soup = readpage(url + str(x+1))
                dongu_no = pullfilms(dongu_no, current_soup)
            # Dosyayı kapattık
            file.close()
print(f'{dongu_no-1} Film bulundu. Tüm filmler {csv_name +" dosyasına"} aktarıldı.')
