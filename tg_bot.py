from data_manege import get_data
import requests
import json
import time

# heroku container:push bot -a app-5ka
# heroku container:release bot -a app-5ka

bot_key = '660366956:AAEgjoHagL5tVHearQhc4N6eXBk-r1ZD-tU/'
url = 'https://api.telegram.org/bot'


class Bot:
    def __init__(self, key):
        self.url = url + key

    def run(self):
        update_id = self.getUpdates()['result'][-1]['update_id']
        while True:
            response = self.getUpdates()

            if bool(response['ok']):
                result = response['result'][-1]
                if update_id == result['update_id']:
                    time.sleep(0.5)
                    continue

                update_id = result['update_id']
                chat_id = result['message']['chat']['id']
                text = result['message']['text']

                self.send_items(chat_id, text)

    def send_items(self, chat_id, key='Чипсы'):
        item_list = get_data('innopolis')
        text = ''
        for item in item_list:
            if str(item['name']).lower().find(key.lower()) != -1:
                text = '{0}p. - {1}'.format(item['params']['special_price'], item['name'])
                self.sendMessage(chat_id, text)
        if not text:
            self.sendMessage(chat_id, 'Items is not found')

    def getUpdates(self):
        return json.loads(requests.get(self.url + 'getUpdates').text)

    def sendMessage(self, chat_id, text):
        requests.get(self.url + 'sendMessage?chat_id={0}&text={1}'.format(chat_id, text))


if __name__ == "__main__":
    bot = Bot(bot_key)
    bot.run()
