import arrow
from datetime import datetime, timedelta, date, timezone
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from typing import Collection
from pandas import DataFrame
import requests
import csv
import sys
import os
# Hem temiz bir başlangıç hem de yeniden başlatmalarda Press any key.. mesajını kaldırmak için.
os.system('cls')
run_time = datetime.now().strftime('%d%m%Y%H%M%S')
print(f'Session hash: #{run_time}')


def test_pause():
    os.system('echo Test için durduruluyor. & pause >nul')


def filtre_sor():
    # Filter req
    while True:
        filter_yn = input(f"> Listeye filtre uygulanacak mı? [Y/N]: ").lower()
        if filter_yn == "y":
            w_filter = True
            logging('Listeye filtre uygulanacak.')
            filter_empty_items = 0
            while True:
                decadeyear_dory = input(
                    f"\n> Want Decade or Year filter? [D/Y/N]: ").lower()
                if decadeyear_dory == "d":
                    # Çekmek yerine ürettik.
                    decade_year = 1870  # min decade year
                    max_multiply = 16  # 16*10 + 1870
                    decade_years = []
                    decade_nums = []
                    decade_num = 0
                    for i in range(max_multiply):
                        # blank = ' ' if i in range(10) else ''
                        blank = ' ' if i < 10 else ''
                        print(f'[{decade_num}] {blank}{decade_year}s')
                        decade_years.append(int(decade_year))
                        decade_year += 10
                        decade_nums.append(int(decade_num))
                        decade_num += 1
                    i_decadeyear = int(input(f"> Decade [Num]: "))
                    print(
                        f'Selected: [{i_decadeyear}]: {decade_years[i_decadeyear]}s\n')
                    msg_decadeyear = f'  \u25E6 Decade:  [{i_decadeyear}]: {decade_years[i_decadeyear]}s\n'
                    w_decadeyear = f"/decade/{decade_years[i_decadeyear]}s"
                    decadeyear_confirm = True
                elif decadeyear_dory == "y":
                    while True:
                        i_decadeyear = int(input(f"> Year [1870-2029]: "))
                        msg_decadeyear = f'   Year: {i_decadeyear}\n'
                        w_decadeyear = f"/year/{i_decadeyear}"
                        decadeyear_confirm = True
                        # Linkler 1870 ve 2029'a kadar çalışıyor.
                        if i_decadeyear >= 1870 and i_decadeyear <= 2029:
                            print(f'Selected: {i_decadeyear}\n')
                            break
                        else:
                            print('Belirtilen aralıkta seçim yapınız.')
                elif decadeyear_dory == "n":
                    w_decadeyear = ''
                    msg_decadeyear = ''
                    print('Decade veya year filtresi uygulanmayacak.\n')
                    filter_empty_items = 1
                    decadeyear_confirm = True
                else:
                    print("Anlaşılmadı. Tekrar deneeyin.")
                    decadeyear_confirm = False
                # decade ve year işlemleri tamamsa çıkalım
                if decadeyear_confirm:
                    break
            while True:
                genre_dory = input(f"> Want genre filter? [Y/N]: ").lower()
                if genre_dory == "y":

                    # Buradaki 3 bizim 4.ula gitmemize yarayacak
                    genre_filter_name, genre_filter_adress, filter_num = search_filters(
                        3)
                    # Gelen filtre adresini düzenliyoruz. Son kısmını alıyoruz
                    strip_genre = genre_filter_adress.replace(
                        f'/{user_name}/list/{list_name}/detail', "")
                    msg_genre = f'  \u25E6 Genre:   [{filter_num}]: {genre_filter_name}\n'
                    w_genre = strip_genre
                    genre_confirm = True
                elif genre_dory == "n":
                    w_genre = ''
                    msg_genre = ''
                    print('Genre filtresi uygulanmayacak.\n')
                    filter_empty_items += 1
                    genre_confirm = True
                else:
                    print("Anlaşılmadı. Tekrar deneyin.")
                    genre_confirm = False
                if genre_confirm:
                    break
            while True:
                sortby_dory = input(f"> Want Sort By filter? [Y/N]:").lower()
                if sortby_dory == "y":
                    # Buradaki 1 bizim 2. ula gitmemize yarayacak.
                    sortby_filter_name, sortby_filter_adress, filter_num = search_filters(
                        1)
                    # Gelen filtre adresini düzenliyoruz. Son kısmını alıyoruz
                    strip_sortby = sortby_filter_adress.replace(
                        f'/{user_name}/list/{list_name}/detail', "")
                    msg_sortby = f'  \u25E6 Sort By: [{filter_num}]: {sortby_filter_name}\n'
                    w_sortby = strip_sortby
                    sortby_confirm = True
                elif sortby_dory == "n":
                    w_sortby = ''
                    msg_sortby = ''
                    print('Sort By filtresi uygulanmayacak.\n')
                    filter_empty_items += 1
                    sortby_confirm = True
                else:
                    sortby_confirm = False
                    print("Anlaşılmadı. Tekrar deneyin.")
                if sortby_confirm:
                    break
            # Filtre elemanları bittikten sonra while için filtre onayı
            filter_confirm = True
        # Filtre istemezse
        elif filter_yn == "n":
            w_filter = False
            w_decadeyear, w_genre, w_sortby = '', '', ''
            msg_decadeyear, msg_genre, msg_sortby = '', '', ''
            filter_empty_items = 3
            filter_confirm = True
            logging('Listeye filtre uygulanmayacak.')
        # Filtre isteyip istemediği anlaşılmayınca
        else:
            filter_confirm = False
            print("Tam anlayamadık? Tekrar deneyin.")
            logging('Kullanıcı soruya cevap veremedi.')
        # While döngüsünden çıkmak için.
        if filter_confirm:
            break
    all_filtres = f'{w_decadeyear}{w_genre}{w_sortby}'
    filtres_msg = f'{msg_decadeyear}{msg_genre}{msg_sortby}'
    return all_filtres, w_filter, filtres_msg, filter_empty_items


def search_filters(ul_num):
    # genre 3, sortby 1
    # Sıralama adreslerini çekmek.
    # Filtre yöntemlerinden listenin sıralama yöntemleri olan ul etiketini yani 2.srıadaki ul'u seçtik.
    ul_filters = soup.find_all(
        'ul', attrs={'class': 'smenu-menu'})[ul_num].find_all("li")
    current_filter_number = 0
    # İSimler ve filtreler için boş küme oluşturduk

    filter_names, filter_adresses = [], []
    for current_li in ul_filters:
        try:
            current_filter_name = current_li.find('a').text
        except:
            current_filter_name = current_li.text
        finally:
            filter_names.append(str(current_filter_name))
        try:
            current_filter_adress = current_li.find('a')['href']
        except:
            current_filter_adress = current_li.find('href')
        finally:
            filter_adresses.append(str(current_filter_adress))

        blank = ' ' if current_filter_number < 10 else ''
        print(f'[{current_filter_number}]: {blank}{current_filter_name}')
        current_filter_number += 1
    filter_num = int(input("> Filter [Num]: "))
    print(f'Selected: [{filter_num}]: {filter_names[filter_num]}\n')
    return filter_names[filter_num], filter_adresses[filter_num], filter_num


def signature(x):
    # x: 0 ilk, 1 son
    try:
        if x == True:

            # İlk imza gösteriminde öncesini temizle
            os.system('cls')
            print('Your Inputs;', end='')
            if w_filter and filter_empty_items < 3:
                print(
                    f'\u00B7 User: {user_name}\n\u00B7 List: {list_name}\n\u00B7 Filtre uygulaması: Var\n{filtres_msg}')
            else:
                print(
                    f'\n\u00B7 User: {user_name}\n\u00B7 List: {list_name}\n\u00B7 Filtre uygulaması: Yok\n')

            # Liste sayfasından bilgiler çekmek.
            try:
                print('List info;')
                # > Liste sahibin ismini çektik
                search_listBy = soup.select("[itemprop=name]")[0].text
                print(f'\u00B7 List by {search_listBy} (@{user_name})')
                # > Liste başlığının ismini çektik
                search_listTitle = soup.select("[itemprop=title]")[0].text
                print(f'\u00B7 List title "{search_listTitle}" ')
                # > Liste oluşturulma tarihi
                search_listPtime = soup.select(".published time")[0].text
                # > arrow: https://arrow.readthedocs.io/en/latest/
                listPtime = arrow.get(search_listPtime)
                print(f'\u00B7 Published: {listPtime.humanize()}')
                # < or: print(f'Published: {listPtime.humanize(granularity=["year","month", "day", "hour", "minute"])}')
                # > utcnow: https://newbedev.com/python-utc-datetime-object-s-iso-format-doesn-t-include-z-zulu-or-zero-offset
                # now_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                # s = arrow.get(now_time) | time_x = s-f | print(f'Time since publication: {time_x}')
                # > Search list update time
                try:
                    search_listUtime = soup.select(".updated time")[0].text
                    listUtime = arrow.get(search_listUtime)
                    msg_Utime = listUtime.humanize()
                except:
                    msg_Utime = 'No editing'
                finally:
                    print(f'\u00B7 Updated: {msg_Utime}')
            except:
                logging(
                    'Film sahibi görünür adı ve liste adı istenirken hata oluştu.')
        else:
            print(
                f'\nFilename: {csv_name}\nFilm sayısı: {dongu_no-1}\nTüm filmler {csv_name + " dosyasına"} aktarıldı.')
            # Seçili olan filtreyi yazdırdık.
            try:
                search_selected_decadeyear = current_soup.select(
                    ".smenu-subselected")[3].text
                print(
                    f'Filtered as {search_selected_decadeyear} movies only was done by')
                search_selected_genre = current_soup.select(
                    ".smenu-subselected")[2].text
                print(f'Filtered as {search_selected_genre} only movies')
                search_selected_sortby = current_soup.select(
                    ".smenu-subselected")[0].text
                print(f'Movies sorted by {search_selected_sortby}')
            except:
                logging("Film filtre bilgileri alınamadı..")

        log = 'İmza yazdırma işlemleri tamamlandı.'
    except:
        print('İmza seçimi başarısız.')
        log = 'İmza yüklenemedi. Program yine de devam etmeyi deneyecek.'
    finally:
        logging(log)


def rst():
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except:
        log = 'Programın yeniden başlatılmaya çalışılması başarısız.'
        print(log)
        logging(log)


def dir_check(l, e):
    # Buradaki ifler tekli kontrol yapmamıza yarar
    # < Örneğin e'yi false yollarım ve sadece l'yi çekebilirim.
    # l= logdir_name, e = exdir_name
    if l:
        # Log Dir
        if os.path.exists(l):
            logging(f'{l} klasörü halihazırda var.')
        else:
            os.makedirs(l)
            logging(f'{l} klasörü oluşturuldu')
            # Oluşturulmaz ise bir izin hatası olabilir
    if e:
        # Exports Dir
        if os.path.exists(e):
            logging(f'{e} klasörü halihazırda var.')
        else:
            os.makedirs(e)
            logging(f'{e} klasörü oluşturuldu')
            # Oluşturulmaz ise bir izin hatası olabilir


def countrooms(r_article):
    try:
        data_count = 0
        for rooms in r_article:
            data_count += 1
        return data_count
    except:
        print('Sayım işlemi başarısız.')


def logging(r_message):
    try:
        f = open(open_log, "a")
        f.writelines(f'{r_message}\n')
        f.close()
    except:
        print('Loglama işlemi başarısız.')


def f_filmsayisi(r_lastPage_No):
    try:
        # > Son sayfaya bağlanmak için bir ön hazırlık.
        lastsoup = readpage(f'{url}{r_lastPage_No}')
        # > Sayfa kodları çekildi.
        lastarticles = lastsoup.find('ul', attrs={
            'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
        lastpage_fcount = countrooms(lastarticles)
        # < Film sayısı öğrenildi.
        # > Toplam film sayısını belirlemek.
        film_sayisi = ((int(r_lastPage_No)-1)*100)+lastpage_fcount
        logging(f"Bilgi: Film sayısı {film_sayisi} olarak bulunmuştur.")
        return film_sayisi
    except:
        print('Film sayısını elde ederken hata.')


def readpage(r_url):
    try:
        page_url = requests.get(r_url)
        # > Sayfa kodları çekildi.
        soup = BeautifulSoup(page_url.content.decode('utf-8'), 'html.parser')
        logging(f'Trying connect to: {r_url}')
        return soup
    except:
        print('Connection to address failed.')


def pullfilms(r_count, r_soup):
    try:
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
    except:
        print('Film bilgilerini elde ederken bir hatayla karşılaşıldı.')


def check_user():
    try:
        user_displayname = visit_profile.select(".title-1")[0].text
        print(f'Found it: {user_displayname}')
        logging(f'{user_name} kullanıcısı bulundu: {user_displayname}')
        user_available = True
    except:
        print('Kullanıcı bulunamadı. Tekrar deneyin.')
        logging(f'{user_name} kullanıcısı bulunamadı.')
        user_available = False
    finally:
        return user_available


# > Saf domain'in parçalanarak birleştirilmesi
url_protocol, site_url = "https://", "letterboxd.com/"
domain = url_protocol + site_url
# Gerekli dizin ve dosya isimlendirmesi.
exdir_name, logdir_name, = "exports", "logs"
# Burada loh dosyasına oturum onaylanana kadar geçici bir isimlendirme atanır.
open_log = f'{logdir_name}/{run_time}.txt'
# Log klasörünün kontrolü
dir_check(logdir_name, False)

while True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    user_name = str(input("> Username(Not display name): ")).lower()
    # Kullanıcı mevcutmu bakıyoruz
    visit_profile = readpage(f'{domain}{user_name}')
    user_available = check_user()
    if user_available:
        break
# > Dosya çakışma sorunları için farklı isimler ürettik.
csv_name = f"{user_name}-({run_time})"
# Artık log ismi karışmaması için log dosyasının ismini değiştik.
# Os rename ile dizin belirterek dosya taşınabilir
approved_session = f'{logdir_name}/{csv_name}.txt'
os.rename(open_log, approved_session)
open_log = approved_session
open_csv = f'{exdir_name}/{csv_name}.csv'
list_name = str(input("> Listname(Domain): ")).lower()
# Misafir girişi için url oluşturuluyor
pure_url = f'{domain}{user_name}/list/{list_name}/detail/'
soup = readpage(pure_url)
# Filtrelerin çekilmesi ve domaine uygulanması
all_filtres, w_filter, filtres_msg, filter_empty_items = filtre_sor()
url = f'{pure_url}{all_filtres}page/'
logging(f'Filtreler: {all_filtres}\nFiltre Url\'ye işlendi: {url}')
# Karşılama mesajı, kullanıcının girdiği bilgleri ve girilen bilgilere dayanarak listenin bilgilerini yazdırır.
signature(1)
# > Domain'in doğru olup olmadığı kullanıcıya sorulur, doğruysa kullanıcı enter'a basar ve program verileri çeker.
ent = input(
    f"\u00B7 Link: {pure_url}{all_filtres}\n\n> Press enter to confirm the entered information. (Enter)\n").lower()
if ent == "":
    # Gerekli klasörlerin kontrolü
    dir_check(False, exdir_name)

    # > Burada pure_url ile liste sayfa sayısını elde ediyoruz ve aşağısında film toplamı sayısını hesaplıyoruz
    logging('Saf sayfaya erişim başlatılıyor.')
    try:
        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
        logging('Bilgi: Listedeki sayfa sayısı denetleniyor..')
        lastPage_No = soup.find(
            'div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text
        logging(
            f'Bilgi: Liste birden çok sayfaya {lastPage_No} sayfaya sahiptir.')
        f_filmsayisi(lastPage_No)
    except:
        # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        lastPage_No = 1
        f_filmsayisi(lastPage_No)
        logging('Bilgi: Birden fazla sayfa yok, bu liste tek sayfadır.')
    finally:
        logging(
            f'Saf sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPage_No} olduğu öğrenildi.')

    # Konumda klasör yoksa dosya oluşturmayacaktır.
    with open(f'{open_csv}', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Sıra", "Filmİsmi", "YayınYılı"])
        # Filmleri çekiyoruz
        dongu_no = 1
        # x sıfırdan başlıyor
        for x in range(int(lastPage_No)):
            logging(f'Connecting to: {url}{str(x+1)}')
            current_soup = readpage(f'{url}{str(x+1)}')
            dongu_no = pullfilms(dongu_no, current_soup)
        # Açtığımız dosyayı manuel kapattık
        file.close()
    logging(f'Success!')
    signature(0)
    rst()
else:
    cancel_log = "Bilgileri doğrulamadığınız için oturum iptal edildi."
    print(cancel_log)
    logging(cancel_log)
    rst()


# to:do
# source.find_all(string=["Text","Text2"])
