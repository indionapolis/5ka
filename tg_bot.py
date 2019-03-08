from data_manege import get_data
import requests
import json
import time
import urllib

# heroku container:push bot -a app-5ka
# heroku container:release bot -a app-5ka

TOKEN = '660366956:AAEgjoHagL5tVHearQhc4N6eXBk-r1ZD-tU'
URL = f'https://api.telegram.org/bot{TOKEN}/'

MENU_KEYBOARD = dict(
    keyboard=[
        [
            dict(text='🗄 Категории')
        ]
    ],
    resize_keyboard=True
)

MENU_KEYBOARD = json.dumps(MENU_KEYBOARD)


class Bot:
    def __init__(self, url):
        self.url = url

    def run(self):

        last_update_id = None
        response = self.get_updates()

        if response['ok'] == 'true':
            result = response['result']
            last_update_id = result[-1]['update_id']

        while True:
            response = self.get_updates(last_update_id)

            if bool(response['ok']):
                result = response['result']
                if len(result) > 0:
                    last_update_id = result[-1]['update_id'] + 1
                    try:
                        self.handle(result)
                    except Exception:
                        import traceback, datetime, os

                        with open(os.path.dirname(__file__) + '/bot_error.log', 'a') as logger:
                            logger.write(f'{datetime.datetime.now()}:\n\n'
                                         f'{traceback.format_exc().encode("ascii", "ignore").decode("ascii")}\n\n')
                        continue
                time.sleep(0.5)

    def handle(self, result):
        for event in result:

            chat_id = event['message']['chat']['id']

            try:
                # if we've got not a text
                message_text = event['message']['text']
            except KeyError:
                self.send_message(chat_id, 'Не знаю как реагировать.')
                continue

            text = message_text

            if message_text == '/start':
                self.send_menu(chat_id)

            # debug, usage: send get $post to get post by id=$post
            # elif 'get' in message_text:
            #     self.send_post(chat_id, int(text.split(' ')[1]))

            elif message_text == '🗄 Категории':
                self.send_message(chat_id, 'no')
            else:
                self.send_category(chat_id, text)

    def get_updates(self, offset=None):
        return json.loads(
            requests.get(self.url + 'getUpdates?timeout=100{}'.format('&offset=' + str(offset) if offset else '')).text)

    def send_message(self, chat_id, text, keyboard=None):
        text = urllib.parse.quote_plus(text)
        params = 'sendMessage?chat_id={0}&text={1}'.format(chat_id, text)
        if keyboard:
            keyboard = urllib.parse.quote_plus(keyboard)
            params += '&reply_markup={}'.format(keyboard)
        requests.get(self.url + params)

    def send_menu(self, chat_id):
        text = 'Привет, попробуй мои функции в меню!'
        self.send_message(chat_id, text, MENU_KEYBOARD)

    def send_category(self, chat_id, key):
        item_list = get_data('innopolis')
        text = ''
        for item in item_list:
            if str(item['name']).lower().find(key.lower()) != -1:
                text = '{0}p. - {1}'.format(item['params']['special_price'], item['name'])
                self.send_message(chat_id, text)
        if not text:
            self.send_message(chat_id, 'Items is not found')




    def edit_message(self, chat_id, message_id, text, keyboard):
        keyboard = urllib.parse.quote_plus(keyboard)
        params = 'editMessageText?chat_id={0}&message_id={1}&text={2}&reply_markup={3}'.format(chat_id, message_id,
                                                                                               text, keyboard)
        requests.get(self.url + params)

    def delete_message(self, chat_id, message_id):
        params = 'deleteMessage?chat_id={0}&message_id={1}'.format(chat_id, message_id)
        requests.get(self.url + params)

    def answer_callback_query(self, callback_query_id, text):
        params = 'answerCallbackQuery?callback_query_id={0}&text={1}'.format(callback_query_id, text)
        requests.get(self.url + params)


    def get_categories_keyboard(self):
        categories = self.database.get_categories()
        keyboard = dict(
            keyboard=[
                [
                    dict(
                        text=categories[option]
                    ),
                    dict(
                        text=categories[len(categories) // 2 + option]
                    ),
                ] for option in range(len(categories) // 2)
            ],
            resize_keyboard=True
        )

        if len(categories) % 2:
            keyboard['keyboard'] += [[dict(text=categories[-1])]]

        keyboard['keyboard'] += [[dict(text='📜 Меню')]]
        return json.dumps(keyboard)


if __name__ == "__main__":
    bot = Bot(URL)
    bot.run()
