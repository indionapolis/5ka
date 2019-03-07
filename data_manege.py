import threading
import requests
import time
import json
import os

cities_location_id = {'innopolis': '5870', 'moscow': '1814'}

url = 'https://5ka.ru/api/special_offers/?records_per_page=400&page=1&all_prev=1'


def _load_data():
    for city, location_id in cities_location_id.items():
        cookie = {'location_id': location_id}
        file_name = os.getcwd() + '/data_{}.json'.format(city)
        response = requests.get(url=url, cookies=cookie)
        data = json.loads(response.text)
        with open(file_name, 'w') as file:
            json.dump(data, file)


class _DataUpdate(threading.Thread):
    def run(self):
        while True:
            _load_data()
            time.sleep(60*60*12)


def get_data(city='innopolis'):
    try:

        cookie = {'location_id': cities_location_id[city]}
        file_name = os.getcwd() + '/data_{}.json'.format(city)

        with open(file_name, 'r') as file:
            data = json.load(file)

    except KeyError:

        print('city: {} is not available now'.format(city))
        exit(0)

    except FileNotFoundError:

        response = requests.get(url=url, cookies=cookie)
        data = json.loads(response.text)
        with open(file_name, 'w') as file:
            json.dump(data, file)

    return data['results']


_DataUpdate().start()