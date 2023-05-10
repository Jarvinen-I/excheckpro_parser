import requests
import lxml
import re
import csv
import time
import io
from bs4 import BeautifulSoup as BS


def get_data():
    with io.open('excheckpro_data.csv', 'a', encoding='cp1251') as file:
        writer = csv.writer(file, delimiter=';', lineterminator='\n')
        writer.writerow(
            (
                'Компания',
                'Адрес',
                'Основной вид деятельности',
                'Телефоны',
                'Почта',
                'Реквизиты',
                'Виды лицензируемой деятельности'
            )
        )

    url = 'https://excheck.pro/companies?by=activity&code=42.11'
    headers = {
        'accept': '*/*',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    }

    response = requests.get(url=url, headers=headers, timeout=7)
    soup = BS(response.text, 'lxml')
    pages_count = int(soup.find('ul', class_='pagination justify-content-center mt-3 mb-0').find_all('a')[-1].text) #484
    count = 0

    while True:
        try:
            for page in range(1, pages_count + 1):
                url = f'https://excheck.pro/companies?by=activity&code=42.11&page={page}'
                response = requests.get(url=url, headers=headers, timeout=7)
                soup = BS(response.text, 'lxml')
                companies_cards = soup.find('table', class_='table table-lg').find('tbody').find_all('tr')

                for card in companies_cards:
                    company = card.find_all('td')[-1]
                    company_title = company.find('a').text
                    company_address = company.find('div').text
                    url = 'https://excheck.pro' + company.find('a').get('href')
                    response = requests.get(url=url, headers=headers, timeout=7)
                    soup = BS(response.text, 'lxml')
                    card_data = soup.find('section', class_='info-columns').find_all('div')
                    main_activity = 'Строительство автомобильных дорог и автомагистралей'
                    phone_numbers = [i.get('href').split(':')[-1] for i in soup.find('section', \
                        id='contacts-section').find('div', class_='col').find_all('a')]

                    emails = '\n'.join([i for i in [i.text for i in soup.find('section', id='contacts-section').find_all('a', \
                              href=re.compile('maito'))]])
                    if emails.strip() == '':
                        emails = 'Нет данных'

                    requisites = '\n'.join([i for i in [f"{i.find('td').text}: {i.find('a').text}" for i in soup.find('section', \
                                  id='details-section').find('table').find('tbody').find_all('tr')]])

                    try:
                        licensed_activities = '\n'.join([i + ';' for i in [i.find('td').text for i in soup.find('table', \
                            class_='table caption-top').find('tbody').find_all('tr')]])
                    except:
                        licensed_activities = 'Нет данных'

                    for i in phone_numbers:
                        if '/company' in i:
                            link = 'https://excheck.pro' + i
                            response = requests.get(url=link, headers=headers, timeout=7)
                            soup = BS(response.text, 'lxml')
                            data_from_link = [i.get('href').split(':')[-1] for i in soup.find('section', \
                                              class_='container-lg pt-4 pb-5').find('div', \
                                              class_='row').find('div', class_='col').find_all('a')]

                    phone_numbers = '\n'.join([i for i in phone_numbers])
                    if phone_numbers.strip() == '':
                        phone_numbers = 'Нет данных'

                    with io.open('excheckpro_data.csv', 'a', encoding='cp1251') as file:
                        writer = csv.writer(file, delimiter=';', lineterminator='\n')
                        writer.writerow(
                            (
                                company_title,
                                company_address,
                                main_activity,
                                phone_numbers,
                                emails,
                                requisites,
                                licensed_activities
                            )
                        )
                    count += 1
                    print(f'[+] {count}')
            time.sleep(1)
        except requests.exceptions.Timeout:
            print("Timeout occurred")
        if count >= pages_count:
            print('[+] Работа завершена')
            break


def main():
    get_data()


if __name__ == '__main__':
    main()
