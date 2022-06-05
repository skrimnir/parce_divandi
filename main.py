from bs4 import BeautifulSoup
import requests
import sqlite3
import re


divandi = 'https://www.divandi.ru/dizaynery-i-dizayn-studii'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.132 YaBrowser/22.3.1.892 Yowser/2.5 Safari/537.36'}


def get_html(address):
    html_website = requests.get(address, headers=headers)
    return html_website



def get_contaсt(html):
    soup = BeautifulSoup(html, 'html.parser')
    items_a = soup.find_all('a')
    return items_a


def get_catalog_websit(divandi):
    catalog_list = []
    page = 1
    while True:
        divandi_plus_page = divandi
        if page != 1:
            divandi_plus_page = divandi + '/stranica-' + str(page)
        html = get_html(divandi_plus_page)
        file_list = get_contaсt(html.text)
        if len(file_list) < 158: # 157 - это кол-во элементов на стр где список сайтов пуст
            break
        page += 1
        for i in file_list:
            if 'http://' in i["href"]:
                website = i["href"]
                if 'divandi' not in website and website not in catalog_list and 'instagram' not in website:
                    catalog_list.append(website)
    return catalog_list
    # return print(len(catalog_list)), print(page), print(catalog_list)


def parse():
    resultat = {}
    catalog_list = get_catalog_websit(divandi)
    exception_list = []
    exception_list_2 = []
    for website in range(int(len(catalog_list))):
        address = catalog_list[website]
        try:
            html = get_html(address)
        except requests.exceptions.ConnectionError:
            continue
        file_list = get_contaсt(html.text)
        tel_list = ''
        email_list = ''
        try:
            for i in file_list:
                if 'tel' in i["href"]:
                    o = i.text
                    p = ''.join(c for c in o if c.isdecimal())
                    if p[0:1] == '7':
                        p = '+' + p
                    if len(p) > 3 and p[-1] ==',':
                        p = p[:-1]
                    tel_list = p
                if 'mailto' in i["href"]:
                    email_list = i["href"]
                    email_list = email_list[7:]
                resultat[address] = tel_list, email_list
        except KeyError:
            exception_list.append(address)
            address_contacts = address + '/contact'
            html = get_html(address_contacts)
            file_list = get_contaсt(html.text)
            tel_list = ''
            email_list = ''
            try:
                for i in file_list:
                    if 'tel' in i["href"]:
                        o = i.text
                        p = ''.join(c for c in o if c.isdecimal())
                        if p[0:1] == '7':
                            p = '+' + p
                        if len(p) > 3 and p[-1] == ',':
                            p = p[:-1]
                        tel_list = p
                    if 'mailto' in i["href"]:
                        email_list = i["href"]
                        email_list = email_list[7:]
                    resultat[address] = tel_list, email_list
            except KeyError:
                address_contacts = address + '/contacts'
                html = get_html(address_contacts)
                file_list = get_contaсt(html.text)
                tel_list = ''
                email_list = ''
                try:
                    for i in file_list:
                        if 'tel' in i["href"]:
                            o = i.text
                            p = ''.join(c for c in o if c.isdecimal())
                            if p[0:1] == '7':
                                p = '+' + p
                            if len(p) > 3 and p[-1] == ',':
                                p = p[:-1]
                            tel_list = p
                        if 'mailto' in i["href"]:
                            email_list = i["href"]
                            email_list = email_list[7:]
                        resultat[address] = tel_list, email_list
                except KeyError:
                    exception_list_2.append(address)
                    continue

        try:
            if resultat[address] == ('', ''):
                soup = BeautifulSoup(html.text, 'html.parser')
                all_str_at_mail = soup.find_all(string=re.compile('@' and 'mail'))
                if len(all_str_at_mail) >= 1:
                    all_str_at_mail = str(all_str_at_mail[0])
                    all_str_at_mail = all_str_at_mail.split(' ')
                for i in all_str_at_mail:
                    if '@' in i and len(i) < 30:
                        resultat[address] = '', i
        except KeyError:
            continue

    return resultat


def upgreid_db():
    db = sqlite3.connect('database.sqlite')
    cursor = db.cursor()
    blacklist_domain = ['houzz.ru', 'gkamen.com','smartsquare.ru','http://www.greatinterior.ru','']
    parse_dic = parse()
    for key in parse_dic:
        web = f'"{key}"'
        domain_split = re.split('/', web)
        domain = domain_split[2]
        if domain[-1] == '"':
            domain = domain[:-1]
        if 'www' in domain:
            domain = domain[4:]
        if domain in blacklist_domain:
            continue
        telephone_and_email = parse_dic[key]
        cursor.execute(f"SELECT domain FROM Buro WHERE site = '{domain}'")
        if cursor.fetchone() is None:
            cursor.execute(f"INSERT INTO Buro (site, inst, tel, email, country, mail_date, response_date, domain, request) VALUES ({web}, '', '{telephone_and_email[0]}', '{telephone_and_email[1]}', 'RU', '', '', '{domain}', 'divandi')")
            db.commit()
        else:
            print(f"'repeat!' {web}")
    db.close()


upgreid_db()