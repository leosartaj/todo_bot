import time
import json
import requests


TOKEN = '272815511:AAFIGOqKrxKern42hTC8B6zeKXxzT5dTUNA'
URL = 'https://api.telegram.org/bot{}/'.format(TOKEN)


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


def send_message(chat_id, text):
    params = {'text': text, 'chat_id': chat_id}
    url = URL + 'sendMessage'
    get_url(url, params)


def echo_all(updates):
    for update in updates['result']:
        text = update['message']['text']
        chat_id = update['message']['chat']['id']
        send_message(chat_id, text)


if __name__ == '__main__':
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates['result']):
            echo_all(updates)
            last_update_id = get_last_update_id(updates) + 1
        time.sleep(0.5)
