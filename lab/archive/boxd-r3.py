import sys
import csv
import requests
import arrow
import json
from datetime import datetime, timedelta, date, timezone
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from typing import Collection
from pandas import DataFrame
import os  # https://stackoverflow.com/a/48010814
# Term Color NET/lOCAL
try:
    from termcolor import colored, cprint
except:
    from labs.termcolor110.termcolor import colored, cprint


def settings_set():
    if os.path.exists('settings.json'):
        while True:
            try:
                with open("settings.json") as jsonFile:
                    jsonObject = json.load(jsonFile)
                    log_dir_name = jsonObject['log_dir']
                    export_dir_name = jsonObject['export_dir']
                    break
            except Exception as except_msg:
                print(f'Ayarlarınız {except_msg} nedeniyle alınamadı.')
    else:
        while True:
            try:
                print('Ayar dosyası bulunamadı. Lütfen gerekli bilgileri girin.')
                log_dir_name = input('Log directory Name: ')
                export_dir_name = input('Export directory Name: ')
                settings_dict = {
                    'log_dir': log_dir_name,
                    'export_dir': export_dir_name,
                }
                with open('settings.json', 'w') as json_file:
                    json.dump(settings_dict, json_file)
                break
            except Exception as except_msg:
                print(f'Ayarlarınız {except_msg} nedeniyle kaydedilemedi.')
    return log_dir_name, export_dir_name


def test_pause():
    os.system('echo Test için durduruluyor. & pause >nul')


def filtre_sor():
    # Filter req
    while True:
        filter_yn = input(
            f'{uInput_cmd_suf} Listeye filtre uygulanacak mı? [{colored("Y", color="green")}/{colored("N", color="red")}]: ').lower()
        if filter_yn == "y":
            w_filter = True
            logging(f'{info_log_suf}Listeye filtre uygulanacak.')
            filter_empty_items = 0
            while True:
                decadeyear_dory = input(
                    f'\n{uInput_cmd_suf} Want Decade or Year filter? [{colored("D", color="green")}/{colored("Y", color="green")}/{colored("N", color="red")}]: ').lower()
                if decadeyear_dory == "d":
                    # Çekmek yerine ürettik.
                    decade_year = 1870  # min decade year
                    max_multiply = 16  # 16*10 + 1870
                    decade_years = []
                    decade_nums = []
                    for decade_num, i in enumerate(range(max_multiply)):
                        # blank = ' ' if i in range(10) else ''
                        blank = ' ' if i < 10 else ''
                        print(
                            f'[{colored(decade_num, color="cyan")}] {blank}{decade_year}s')
                        decade_years.append(int(decade_year))
                        decade_year += 10
                        decade_nums.append(int(decade_num))
                    while True:
                        i_decadeyear = int(input(
                            f'{uInput_cmd_suf} Decade [{colored("Num", color="cyan")}]: '))
                        if i_decadeyear >= min(decade_nums) and i_decadeyear <= max(decade_nums):
                            print(
                                f'    {colored("Selected:", color="green")} [{colored(i_decadeyear, color="cyan")}]: {decade_years[i_decadeyear]}s\n')
                            msg_decadeyear = f'  \u25E6 Decade:  [{i_decadeyear}]: {decade_years[i_decadeyear]}s\n'
                            w_decadeyear = f"/decade/{decade_years[i_decadeyear]}s"
                            decadeyear_confirm = True
                            break
                        else:
                            print(
                                f'{colored("    Belirtilen onyıllardan satır numarasını girmelisiniz.", color="red")}')
                elif decadeyear_dory == "y":
                    decadeyear_confirm = True
                    while True:
                        i_decadeyear = int(
                            input(f'{uInput_cmd_suf} Year [{colored("1870", color="cyan")}-{colored("2029", color="blue")}]: '))
                        msg_decadeyear = f'Year: {i_decadeyear}\n'
                        w_decadeyear = f"/year/{i_decadeyear}"
                        # Linkler 1870 ve 2029'a kadar çalışıyor.
                        if i_decadeyear >= 1870 and i_decadeyear <= 2029:
                            print(
                                f'{colored("    Selected:", color="green")} {i_decadeyear}\n')
                            break
                        else:
                            print(
                                f'{colored("    Belirtilen aralıkta seçim yapınız.", color="red")}')
                elif decadeyear_dory == "n":
                    w_decadeyear = ''
                    msg_decadeyear = ''
                    print('    Zaman aralığı filtresi uygulanmayacak.\n')
                    filter_empty_items = 1
                    decadeyear_confirm = True
                else:
                    print(
                        f'{colored("    Anlaşılmadı, tekrar deneyin.", color="red")}')
                    decadeyear_confirm = False
                # decade ve year işlemleri tamamsa çıkalım
                if decadeyear_confirm:
                    break
            while True:
                genre_dory = input(
                    f'{uInput_cmd_suf} Want genre filter? [Y/N]: ').lower()
                if genre_dory == "y":

                    # Buradaki 3 bizim 4.ula gitmemize yarayacak
                    genre_filter_name, genre_filter_adress, filter_num = search_filters(
                        3)
                    # Gelen filtre adresini düzenliyoruz. Son kısmını alıyoruz
                    strip_genre = genre_filter_adress.replace(
                        f'/{user_name}/list/{list_name}detail', "")
                    msg_genre = f'  \u25E6 Genre:   [{filter_num}]: {genre_filter_name}\n'
                    w_genre = strip_genre
                    genre_confirm = True
                elif genre_dory == "n":
                    w_genre = ''
                    msg_genre = ''
                    print('    Genre filtresi uygulanmayacak.\n')
                    filter_empty_items += 1
                    genre_confirm = True
                else:
                    print("Anlaşılmadı. Tekrar deneyin.", end='')
                    genre_confirm = False
                if genre_confirm:
                    break
            while True:
                sortby_dory = input(
                    f'{uInput_cmd_suf} Want Sort By filter? [Y/N]:').lower()
                if sortby_dory == "y":
                    # Buradaki 1 bizim 2. ula gitmemize yarayacak.
                    sortby_filter_name, sortby_filter_adress, filter_num = search_filters(
                        1)
                    # Gelen filtre adresini düzenliyoruz. Son kısmını alıyoruz
                    strip_sortby = sortby_filter_adress.replace(
                        f'/{user_name}/list/{list_name}detail', "")
                    msg_sortby = f'  \u25E6 Sort By: [{filter_num}]: {sortby_filter_name}\n'
                    w_sortby = strip_sortby
                    sortby_confirm = True
                elif sortby_dory == "n":
                    w_sortby = ''
                    msg_sortby = ''
                    print('  Sort By filtresi uygulanmayacak.\n')
                    filter_empty_items += 1
                    sortby_confirm = True
                else:
                    sortby_confirm = False
                    print("  Anlaşılmadı. Tekrar deneyin.")
                if sortby_confirm:
                    break
            # Filtre elemanları bittikten sonra while için filtre onayı
            filter_confirm = True
        elif filter_yn == "n":
            w_filter = False
            w_decadeyear, w_genre, w_sortby = '', '', ''
            msg_decadeyear, msg_genre, msg_sortby = '', '', ''
            filter_empty_items = 3
            filter_confirm = True
            logging(f'{info_log_suf}Listeye filtre uygulanmayacak.')
        else:
            filter_confirm = False
            print("Tam anlayamadık? Tekrar deneyin.")
            logging(f'{info_log_suf}Kullanıcı soruya cevap veremedi.')
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
        # Seçimin başlığı var mı
        try:
            filter_sub = current_li.find('span').text
            print(f'{filter_sub}')
            current_filter_number -= 1
        # Seçimin Başlığı yoksa
        except:
            # Dene
            try:
                # İlk 10 Liste elemanı için boşluk ayarlar ve hızalarız
                blank = ' ' if current_filter_number < 10 else ''
                print(f'[{current_filter_number}]: {blank}', end=' ')
                # Liste ismini almayı deneriz
                try:
                    current_filter_name = current_li.find('a').text
                except:
                    current_filter_name = current_li.text
                finally:
                    filter_names.append(str(current_filter_name))
                    print(f'{current_filter_name}')
                # Liste elemanının adresini almayı deneriz.
                try:
                    current_filter_adress = current_li.find('a')['href']
                except:
                    current_filter_adress = current_li.find('href')
                finally:
                    filter_adresses.append(str(current_filter_adress))
            except:
                pass
        current_filter_number += 1
    # Kullanıcı bir eleman seçer
    filter_num = int(input(f'{uInput_cmd_suf} Filter [Num]: '))
    print(f'Selected: [{filter_num}]: {filter_names[filter_num]}\n')
    return filter_names[filter_num], filter_adresses[filter_num], filter_num


def signature(x):
    # x: 0 ilk, 1 son
    try:
        if x == True:

            # İlk imza gösteriminde öncesini temizle
            os.system('cls')
            print(colored('Your Inputs;', color="yellow"))
            if w_filter and filter_empty_items < 3:
                print(
                    f'{mPoint_cmd_suf} User: {user_name}\n{mPoint_cmd_suf} List: {list_name}\n{mPoint_cmd_suf} Filtre uygulaması: Var\n{filtres_msg}')
            else:
                print(
                    f'{mPoint_cmd_suf} User: {user_name}\n{mPoint_cmd_suf} List: {list_name}\n{mPoint_cmd_suf} Filtre uygulaması: Yok\n')

            # Liste sayfasından bilgiler çekmek.
            try:
                print(colored('List info;', color="yellow"))
                # > Liste sahibin ismini çektik
                search_listBy = soup.select("[itemprop=name]")[0].text
                print(f'{mPoint_cmd_suf} List by {search_listBy} (@{user_name})')
                # > Liste başlığının ismini çektik
                search_listTitle = soup.select("[itemprop=title]")[
                    0].text.strip()
                print(f'{mPoint_cmd_suf} List title: {search_listTitle}')
                # Film sayısını yazdırdık.
                print(
                    f'{mPoint_cmd_suf} Number of movies: {f_filmsayisi(f_ListLastPageNo())}')
                # > Liste oluşturulma tarihi
                search_listPtime = soup.select(".published time")[0].text
                # > arrow: https://arrow.readthedocs.io/en/latest/
                listPtime = arrow.get(search_listPtime)
                print(f'{mPoint_cmd_suf} Published: {listPtime.humanize()}')
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
                    print(f'{mPoint_cmd_suf} Updated: {msg_Utime}')
            except:
                logging(
                    f'{err_log_suf}Film sahibi görünür adı ve liste adı istenirken hata oluştu.')
        else:
            print(f'\n{mPoint_cmd_suf} Filename: {csv_name}\n{mPoint_cmd_suf} Film sayısı: {dongu_no-1}\n{mPoint_cmd_suf} Tüm filmler ', end="")
            cprint(open_csv, 'yellow', attrs=[
                   'blink'], end=" dosyasına aktarıldı.\n")

            # Seçili olan filtreyi yazdırdık.
            try:
                search_selected_decadeyear = current_soup.select(
                    ".smenu-subselected")[3].text
                print(
                    f'{mPoint_cmd_suf} Filtered as {search_selected_decadeyear} movies only was done by')
                search_selected_genre = current_soup.select(
                    ".smenu-subselected")[2].text
                print(
                    f'{mPoint_cmd_suf} Filtered as {search_selected_genre} only movies')
                search_selected_sortby = current_soup.select(
                    ".smenu-subselected")[0].text
                print(f'{mPoint_cmd_suf} Movies sorted by {search_selected_sortby}')
            except:
                logging(f'{err_log_suf}Film filtre bilgileri alınamadı..')

        log = f'{info_log_suf}İmza yazdırma işlemleri tamamlandı.'
    except:
        print('İmza seçimi başarısız.')
        log = f'{err_log_suf}İmza yüklenemedi. Program yine de devam etmeyi deneyecek.'
    finally:
        logging(log)


def dir_check(l, e):
    # Buradaki ifler tekli kontrol yapmamıza yarar
    # < Örneğin e'yi false yollarım ve sadece l'yi çekebilirim.
    # l= logdir_name, e = exdir_name
    if l:
        # Log Dir
        if os.path.exists(l):
            logging(f'{info_log_suf}{l} klasörü halihazırda var.')
        else:
            os.makedirs(l)
            logging(f'{info_log_suf}{l} klasörü oluşturuldu')
            # Oluşturulmaz ise bir izin hatası olabilir
    if e:
        # Exports Dir
        if os.path.exists(e):
            logging(f'{info_log_suf}{e} klasörü halihazırda var.')
        else:
            os.makedirs(e)
            logging(f'{info_log_suf}{e} klasörü oluşturuldu')
            # Oluşturulmaz ise bir izin hatası olabilir


def countrooms(r_article):
    try:
        return sum(1 for _ in r_article)
    except:
        print('Sayım işlemi başarısız.')


# None: Kullanıcı log lokasyonunu belirtmese de olur
def logging(r_message, r_loglocation=None):
    try:
        with open(open_log, "a") as f:
            f.writelines(f'{r_message}\n')
    except Exception as e:
        if r_loglocation is not None:
            print(
                f'Loglama işlemi {r_loglocation} konumunda {e} nedeniyle başarısız.')
        else:
            print(f'Loglama işlemi {e} nedeniyle başarısız.')


def readpage(r_url):
    try:
        page_url = requests.get(r_url)
        # > Sayfa kodları çekildi.
        soup = BeautifulSoup(page_url.content.decode('utf-8'), 'html.parser')
        logging(f'{info_log_suf}Trying connect to [{r_url}]')
        return soup
    except:
        print('Connection to address failed.')
        logging(f'{err_log_suf}Connection to address failed [{r_url}]')


# Filmleri çekiyoruz yazıyoruz
def pullfilms(r_count, r_soup):
    try:
        # > Çekilen sayfa kodları, bir filtre uygulanarak daraltıldı.
        articles = r_soup.find('ul', attrs={
            'class': 'poster-list -p70 film-list clear film-details-list'}).find_all("li")
        dongu_no = r_count
        # > Filmleri ekrana ve dosyaya yazdırma işlemleri
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
            print(f'{dongu_no})  {film_adi} ({film_yili})')
            writer.writerow([str(film_adi), film_yili])
            dongu_no += 1
        return dongu_no
    except:
        print('Film bilgilerini elde ederken bir hatayla karşılaşıldı.')


# Kullanıcının var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
def check_user():
    try:
        user_displayname = visit_profile.select(".title-1")[0].text
        print(f'    {colored("Found it: ", color="green")}{user_displayname}')
        logging(
            f'{info_log_suf}{user_name} kullanıcısı bulundu: {str(user_displayname)}', check_user.__name__)
        user_available = True
    except:
        print(colored('    Kullanıcı bulunamadı. Tekrar deneyin.', color="red"))
        logging(f'{info_log_suf}{user_name} kullanıcısı bulunamadı.',
                check_user.__name__)
        user_available = False
    finally:
        return user_available


# Kullanıcının girilen şekilde ir listesinin var olup olmadığını kontrol ediyoruz. Yoksa tekrar sormak için.
def check_user_list():
    try:
        # > bu meta etiketinden veri almayı deniyor eğer yoksa liste değil.
        try:
            meta_test = visit_list.find(
                'meta', property="og:type").attrs['content']
            # Meta etiketindeki bilgi sorgulanır. Sayfanın liste olup olmadığı anlaşışılır
            if meta_test == "letterboxd:list":
                logging(
                    f'{info_log_suf}Meta içeriği girilen adresin bir liste olduğunu doğruladı. Meta içeriği: {meta_test}')
                # Liste ismini alıyoruz.
                c_listname = visit_list.find(
                    'meta', property="og:title").attrs['content']
                print(f'    {colored("Found it: ", color="green")}{c_listname}')
                # Liste yönlendirimesi var mı bakıyoruz
                c_url = visit_list.find(
                    'meta', property="og:url").attrs['content']
                if c_url == visit_list_url:
                    logging(f'{info_log_suf}Liste adresi yönlendime içermiyor.')
                    c_url = visit_list_url
                else:
                    print(
                        f'[{colored("!", color="yellow")}] Girdiğiniz liste linki eskimiştir, muhtemelen liste ismi yakın bir zamanda değişildi.')
                    print(
                        f'    {colored(visit_list_url, color="yellow")} adresini değiştirdik.')
                    print(
                        f'    {colored(c_url, color="green")} adresinden devam ediyoruz.')
                logging(
                    f'{info_log_suf}{list_name} listesi bulundu: {c_listname}')
                c_list_available = True
        except:
            print("    Bu kullanıcının böyle bir listesi yok.")
            c_url = ""
            c_list_available = False

    except:
        c_list_available = False
    finally:
        return c_list_available, c_url


def f_ListLastPageNo():  # Listenin son sayfasını öğren
    try:
        # > Not: Sayfa sayısını bulmak için li'leri sayma. Son sayıyı al.
        # > Son'linin içindeki bağlantının metnini çektik. Bu bize kaç sayfalı bir listemiz olduğunuz verecek.
        logging(f'{info_log_suf}Listedeki sayfa sayısı denetleniyor..')
        lastPage_No = soup.find(
            'div', attrs={'class': 'paginate-pages'}).find_all("li")[-1].a.text
        logging(
            f'{info_log_suf}Liste birden çok sayfaya ({lastPage_No}) sahiptir.')
        f_filmsayisi(lastPage_No)
    except:
        # > Listede 100 ve 100'den az film sayısı olduğunda sayfa sayısı için bir link oluşturulmaz.
        lastPage_No = 1
        f_filmsayisi(lastPage_No)
        logging(f'{info_log_suf}Birden fazla sayfa yok, bu liste tek sayfadır.')
    finally:
        logging(
            f'{info_log_suf}Saf sayfa ile iletişim tamamlandı. Listedeki sayfa sayısının {lastPage_No} olduğu öğrenildi.')
        return lastPage_No


def f_filmsayisi(r_lastPage_No):  # Film sayısını öğreniyoruz
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
        logging(
            f"{info_log_suf}Listedeki film sayısı {film_sayisi} olarak bulunmuştur.")
        return film_sayisi
    except:
        print('Film sayısını elde ederken hata.')
        logging(f'{err_log_suf}Film sayısı elde edilirkren hata oluştu.s')


def rst():  # Porgramı yeniden başlat
    try:
        os.system('echo Press and any key to reboot & pause >nul')
        os.system('echo Confirm reboot press any key again & pause >nul')
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    except:
        log = 'Programın yeniden başlatılmaya çalışılması başarısız.'
        print(log)
        logging(err_log_suf + log)


# > Hem temiz bir başlangıç hem de yeniden başlatmalarda Press any key.. mesajını kaldırmak için.
# > cprint ASCII Okuyabilmesi için program başlarken bir kere color kullanıyoruz: https://stackoverflow.com/a/61684844
os.system('color & cls')
# > Saf domain'in parçalanarak birleştirilmesi
url_protocol, site_url = "https://", "letterboxd.com/"
domain = url_protocol + site_url
# Mesajlar, Log Mesaj atamaları
uInput_cmd_suf = f'[{colored(">", color="green")}]'
mPoint_cmd_suf = '[' + colored(u"\u00B7", color="cyan") + ']'
err_cmd_suf = f'[{colored("!", color="red")}]'
info_log_suf = "Bilgi: "
err_log_suf = "Hata: "
cancel_log = "Bilgileri doğrulamadığınız için oturum iptal edildi."
# > Run time check - Generate session hash
run_time = datetime.now().strftime('%d%m%Y%H%M%S')
print(f'[{colored("#", color="yellow")}] Session hash: ', end="")
cprint(run_time, 'yellow', attrs=['blink'])
log_dir_name, export_dir_name = settings_set()
# > Log dosyasının konumunu içeren bir değişken
open_log = f'{log_dir_name}/{run_time}.txt'
# > Log klasörünün kontrolü
dir_check(log_dir_name, False)
print(f'[{colored("#", color="yellow")}] Log location created: ', end="")
cprint(open_log, 'yellow', attrs=['blink'])


while True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    user_name = str(
        input(f'{uInput_cmd_suf} Username(Not display name): ')).lower()
    # Kullanıcı mevcutmu bakıyoruz
    visit_profile = readpage(f'{domain}{user_name}')
    user_available = check_user()
    if user_available:
        break

# > Dosya çakışma sorunları için farklı isimler ürettik.
csv_name = f"{user_name}-({run_time})"
# Artık log ismi karışmaması için log dosyasının ismini değiştik.
# Os rename ile dizin belirterek dosya taşınabilir
try:
    approved_session = f'{log_dir_name}/{csv_name}.txt'
    os.rename(open_log, approved_session)
    open_log = approved_session
    print(f'[{colored("#", color="yellow")}] Username added to log file: ', end="")
    cprint(open_log, 'yellow', attrs=['blink'])
except Exception as except_msg:
    print(f"Log dosyasının ismi {except_msg} nedeniyle değiştirilemedi.")
open_csv = f'{export_dir_name}/{csv_name}.csv'


while True:
    # > Kullanıcı eğer domainden değilde direkt olarak girerse yazıyı küçültüyoruz.
    list_name = str(
        input(f'{uInput_cmd_suf} Listname(Domain): ')).lower()
    # Kullanıcının böyle bir listesi mevcutmu bakıyoruz
    visit_list_url = f'{domain}{user_name}/list/{list_name}/'
    visit_list = readpage(visit_list_url)
    userlist_available, approved_list_url = check_user_list()
    # Listenin asıl ismi
    # Approverd boş geldiğinde boşluk değerini değiştirmez
    list_name = approved_list_url.replace(f'{domain}{user_name}/list/', "")
    if userlist_available:
        break

# Misafir girişi için url oluşturuluyor
# approved_list_url https://letterboxd.com/username/list/listname/
pure_url = f'{approved_list_url}detail/'
soup = readpage(pure_url)
# Filtrelerin çekilmesi ve domaine uygulanması
all_filtres, w_filter, filtres_msg, filter_empty_items = filtre_sor()
# Filtreler varsa URL'e işleniyor
url = f'{pure_url}{all_filtres}page/'
print(f'url: {url}')
# Karşılama mesajı, kullanıcının girdiği bilgleri ve girilen bilgilere dayanarak listenin bilgilerini yazdırır.
signature(1)
# > Domain'in doğru olup olmadığı kullanıcıya sorulur, doğruysa kullanıcı enter'a basar ve program verileri çeker.
print(f'{mPoint_cmd_suf} Link: {pure_url}{all_filtres}')
ent = input(
    f'\n{uInput_cmd_suf} Press enter to confirm the entered information. (Enter)')
if ent == "":
    print(colored("    Liste bilgilerini onayladınız.", color="green"))
    logging(f'{info_log_suf}Saf sayfaya erişim başlatılıyor.')
    # > Soupta artık filtreli adresin bilgiler var.
    soup = readpage(pure_url+all_filtres)
    lastPage_No = f_ListLastPageNo()
    # Export klasörünün kontrolü
    dir_check(False, export_dir_name)
    # Konumda klasör yoksa dosya oluşturmayacaktır.
    with open(f'{open_csv}', 'w', newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Year"])
        # Filmleri çekiyoruz
        dongu_no = 1
        # x sıfırdan başlıyor
        print("\nListedeki filmler:")
        for x in range(int(lastPage_No)):
            logging(f'Connecting to: {url}{str(x+1)}')
            current_soup = readpage(f'{url}{str(x+1)}')
            dongu_no = pullfilms(dongu_no, current_soup)
        # Açtığımız dosyayı manuel kapattık
        file.close()
    logging(f'{info_log_suf}Success!')
    signature(0)
else:
    print(cancel_log)
    logging(info_log_suf + cancel_log)

rst()


# to:do
# source.find_all(string=["Text","Text2"])
