import time
import json
import requests

from dbhelper import DBHelper

TOKEN = '272815511:AAFIGOqKrxKern42hTC8B6zeKXxzT5dTUNA'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)
DB = DBHelper()


def get_url(url, params=None):
    response = requests.get(url, params=params)
    content = response.content.decode('utf8')
    return content


def get_json(url, params=None):
    content  = get_url(url, params)
    return json.loads(content)


def get_updates(offset=None, timeout=100):
    url = URL + 'getUpdates'
    params = {'timeout': timeout, 'offset': offset}
    return get_json(url, params)


def get_last_update_id(updates):
    return max(int(update['update_id']) for update in updates['result'])


def send_message(chat_id, text, reply_markup=None):
    params = {'text': text,
              'chat_id': chat_id,
              'parse_mode': 'Markdown',
              'reply_markup': reply_markup}
    url = URL + 'sendMessage'
    get_url(url, params)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {'keyboard': keyboard, 'one_time_keyboard': True}
    return json.dumps(reply_markup)


def handle_updates(updates):
    for update in updates['result']:
        text = update['message']['text']
        chat_id = update['message']['chat']['id']
        items = DB.get_items(chat_id)
        if text == '/start':
            send_message(chat_id, 'Welcome to your personal Todo List')
        elif text == '/done':
            send_message(chat_id, 'Mark an item as completed',
                         build_keyboard(items))
        elif text == '/show':
            send_message(chat_id, 'Your TODO List:\n\n')
            send_message(chat_id, '\n'.join(items))
        elif text.startswith('/'):
            continue
        elif text in items:
            DB.delete_item(chat_id, text)
            items = DB.get_items(chat_id)
            send_message(chat_id, 'Item "{}" marked as completed'.format(text))
        else:
            DB.add_item(chat_id, text)
            items = DB.get_items(chat_id)
            send_message(chat_id, 'Item "{}" Added to TODO List'.format(text))


if __name__ == '__main__':
    DB.setup()
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates['result']):
            handle_updates(updates)
            last_update_id = get_last_update_id(updates) + 1
        time.sleep(0.5)
