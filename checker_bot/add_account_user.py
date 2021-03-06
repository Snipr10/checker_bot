import random
import time
from datetime import timedelta

import requests
import asyncio

from django.utils import timezone
from telethon import TelegramClient, events, sync

from checker_bot.settings import country_codes, sms_active_key
from core.models import Sessions


def add_number(bot_api, attempt=0):
    code = 0
    try:
        code = country_codes[attempt]
    except Exception as e:
        code = 0
    get_key = 'https://sms-activate.ru/stubs/handler_api.php?api_key={}&action=getNumber&service=tg&country={}'.format(
        sms_active_key, code)
    key_info = requests.get(get_key)
    # 'ACCESS_NUMBER:325929094:77715984276'
    data_sms_active = key_info.text
    print("key")

    if data_sms_active == 'NO_BALANCE':
        raise Exception('NO_BALANCE')
    if data_sms_active == 'NO_NUMBERS':
        time.sleep(5)
        if attempt + 1 >= len(country_codes):
            return False
        else:
            return add_number(bot_api, attempt + 1)

    try:
        data_split = data_sms_active.split(":")
        phone = data_split[2]
        id = data_split[1]
    except Exception as e:
        if attempt + 1 >= len(country_codes):
            return False
        else:
            return add_number(bot_api, attempt + 1)
    asyncio.set_event_loop(asyncio.SelectorEventLoop())

    try:
        client = TelegramClient(phone, bot_api.api_id, bot_api.api_hash)
        first_name = ['Aaron', 'Abraham', 'Adam', 'Adrian', 'Aidan', 'Alan',
                      'Albert', 'Alejandro', 'Alex', 'Alexander', 'Alfred', 'Andrew', 'Angel', 'Anthony', 'Antonio',
                      'Ashton', 'Austin', 'Georgy', 'Gleb', 'Danila', 'Vladimir', 'Denis',
                      'Yevgeny', 'Ivan', 'Ilia', 'Innokenty', 'Maksim', 'Matvei', 'Matvei', 'Nikolay', 'Pavel',
                      'Svyatoslav', 'Ruslan', 'Semyon', 'Yaroslav', 'Yan', 'Filipp', 'Fedor', 'Timofey', 'Stepan'
                      ]
        last_name = ['Donovan', 'Douglas', 'Dowman', 'Dutton', 'Duncan', 'Dunce', 'Durham', 'Dyson', 'Babcock',
                     'Bargeman', 'Baldwin', 'Bargeman', 'Barnes', 'Becker', 'Birch', 'Carrington', 'Carter', 'Cook',
                     'Conors', 'Elmers', 'Enderson', 'Faber', 'Farrell', 'Flannagan', 'Fleming', 'Foster', 'Fraser',
                     'Gill', 'Goldman', 'Gustman', 'Hamphrey', 'Hardman', 'Harrison', 'Hodges', 'Fedor', 'Freeman',
                     'Fisher'
                     ]
        client.start(phone=phone, force_sms=True, code_callback=lambda: code_callback(id),
                     first_name=first_name[random.randint(0, len(first_name) - 1)],
                     last_name=last_name[random.randint(0, len(last_name) - 1)])
        print('completed_phone')

    except ConnectionError as e:
        print(e)
        print("need proxy")
        deactive_phone(id)
        return False
    except Exception as e:
        print(e)
        deactive_phone(id)
        return False

    try:
        client.edit_2fa(new_password='qweewq123qa')
        print("2fa password: qweewq123qa")
    except Exception:
        print("Can not add new password")

    Sessions.objects.create(name=phone, bot_api_id=bot_api.id,
                            last_parsing=(timezone.now()) + timedelta(minutes=25),
                            created=(timezone.localtime()))
    client.disconnect()
    return True


def code_callback(id):
    try:
        requests.get(
            'https://sms-activate.ru/stubs/handler_api.php?api_key={}&action=setStatus&id={}&status=1'.format(
                sms_active_key, id))
    except Exception as e:
        return None
    key = get_key(id)
    return key


def get_key(id):
    try:
        status_text = get_status(id)
        if status_text == "STATUS_WAIT_CODE":
            time.sleep(5)
            return get_key(id)
        if "STATUS_OK" in status_text:
            return status_text.split(":")[1]
    except Exception as e:
        return None


def get_status(id):
    return requests.get(
        'https://sms-activate.ru/stubs/handler_api.php?api_key={}&action=getStatus&id={}'.format(
            sms_active_key, id)).text


def deactive_phone(id):
    requests.get(
        'https://sms-activate.ru/stubs/handler_api.php?api_key={}&action=setStatus&id={}&status=8'.format(
            sms_active_key, id))


def completed_phone(id):
    requests.get(
        'https://sms-activate.ru/stubs/handler_api.php?api_key={}&action=setStatus&id={}&status=6'.format(
            sms_active_key, id))