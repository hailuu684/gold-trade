import requests
from config import parameters

# Telegram Bot Settings
telegram_bot_token = parameters['telegram_bot_token']
telegram_chat_id_test_2 = parameters['test_2_chat_id']
telegram_chat_id_test_1 = parameters['test_1_chat_id']


def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    data = {'chat_id': telegram_chat_id_test_2, 'text': message}
    response = requests.post(url, data=data)
    return response


def send_tele_gram_message_test_1(message):
    url = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage'
    data = {'chat_id': telegram_chat_id_test_1, 'text': message}
    response = requests.post(url, data=data)
    return response

