import asyncio
import random
import sqlite3
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta

import telethon
from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from telethon import TelegramClient, events, sync
from telethon.errors import FloodWaitError, AuthKeyUnregisteredError, UsernameInvalidError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon import TelegramClient, events, sync
from telethon.errors import FloodWaitError, AuthKeyUnregisteredError, UsernameInvalidError
from telethon.tl.functions.channels import GetFullChannelRequest

from checker_bot.send_message import send_message
from core.elastic.elastic import add_to_elastic_bot_data, delete_from_elastic
from core.models import Sessions, BotApi


def add_user(phone, bot_api):
    asyncio.set_event_loop(asyncio.SelectorEventLoop())

    # client = TelegramClient(phone, bot_api.api_id, bot_api.api_hash, proxy=(socks.HTTP, proxy.ip, proxy.port,
    #                                                                         True, proxy.login,
    #                                                                         proxy.proxy_password))
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
    client.start(phone=phone, force_sms=True,
                 first_name=first_name[random.randint(0, len(first_name) - 1)],
                 last_name=last_name[random.randint(0, len(last_name) - 1)])

    # in prod add password
    # try:
    #     client.edit_2fa(new_password='qweewq123qa')
    #     print("2fa password: qweewq123qa")
    # except Exception:
    #     print("Can not add new password")

    # 25 sleep time
    Sessions.objects.create(name=phone, bot_api_id=bot_api.id,
                            last_parsing=(timezone.now()) + timedelta(minutes=25),
                            created=(timezone.localtime()))


def get_session():
    session = Sessions.objects.filter(Q(last_parsing__isnull=True)
                                      | Q(last_parsing__lte=(timezone.localtime()) - timedelta(minutes=3)),
                                      is_parsing=False, is_active__lte=10
                                      ).order_by('last_parsing').first()
    # if session is not None:
    #     session.is_parsing = True
    #     session.last_parsing = timezone.localtime()
    #     session.save(update_fields=['is_parsing', 'last_parsing'])
    return session


def get_client(session=None, sleep=True):

    asyncio.set_event_loop(asyncio.SelectorEventLoop())
    if session is None:
        session = get_session()
        if session is None:
            return None, None
        now = timezone.localtime()
        session.is_parsing = True
        session.start_parsing = now
        session.last_parsing = now
        session.save(update_fields=['is_parsing', 'start_parsing', 'last_parsing'])

    bot_api = BotApi.objects.filter(id=session.bot_api_id).first()
    if bot_api is None:
        session.is_active = 11
        session.is_parsing = False
        session.save(update_fields=['is_active', 'is_parsing'])
        return get_client()

    # client = TelegramClient(session.name, bot_api.api_id, bot_api.api_hash, proxy=(socks.HTTP, proxy.ip, proxy.port,
    #                                                                                True, proxy.login,
    #                                                                                proxy.proxy_password))

    client = TelegramClient(session.name, bot_api.api_id, bot_api.api_hash)
    try:
        if True:
            try:
                client.connect()
                # client.start(phone='0', code_callback=callback, max_attempts=0)
            except sqlite3.OperationalError as e:
                print('sqlite3' + str(e))
                client.disconnect()
                ban_session(session, 3600)
                return get_client()
            except ConnectionError as e:
                print('ConnectionError')
                ban_session(session, 3600)
                return get_client()
            except FloodWaitError as e:
                print('FloodWaitError')
                ban_session(session, e.seconds)
                return get_client()
            except Exception as e:
                print('Exception BAN')
                session.is_active = session.is_active + 1
                session.save(update_fields=['is_active'])
                return get_client()
            if sleep:
                time.sleep(1)
            return client, session
    except Exception as e:
        print(str(e))
        session.is_parsing = False
        session.save(update_fields=['is_parsing'])
        return None, None


def ban_session(session, seconds):
    try:
        session.is_parsing = False
        session.is_active = 11
        session.banned_until = timezone.localtime() + timedelta(seconds=seconds)
        session.save(update_fields=['is_parsing', 'is_active', 'banned_until'])
    except Exception as e:
        print(str(e) + 'ban_session disconnect')


def status_bot_founded(bot):
    bot.is_founded = False
    bot.is_being_checked = False
    bot.save(update_fields=['is_founded', 'is_being_checked'])


def stop_parsing_bot(bot):
    bot.is_being_checked = False
    bot.save(update_fields=['is_being_checked'])


def disconnect(bot, session, client):
    bot.is_being_checked = False
    bot.save(update_fields=['is_being_checked'])
    session.is_parsing = False
    session.last_parsing = timezone.localtime()
    session.save(update_fields=['is_parsing', 'last_parsing'])


def disconnect_success(bot, session):
    bot.is_being_checked = False
    bot.warnings = 0
    bot.last_check = timezone.localtime()
    if not bot.ready_to_use:
        try:
            add_to_elastic_bot_data(bot)
            bot.ready_to_use = True
        except Exception as e:
            print(e)
        try:
            send_message(bot.user, "Ваш бот добавлен " + str(bot.username))
        except Exception as e:
            print(e)
    bot.save(update_fields=['is_being_checked', 'warnings', 'last_check', 'ready_to_use'])
    session.is_parsing = False
    session.last_parsing = timezone.localtime()
    session.save(update_fields=['is_parsing', 'last_parsing'])


def disconnect_bad(bot, session):
    bot.all_warnings += 1
    bot.warnings += 1
    if not bot.ready_to_use and (bot.warnings == 0 or bot.warnings == 11):
        try:
            send_message(bot.user, "Ваш бот не отвечает " + str(bot.username))
        except Exception as e:
            print(e)
    bot.is_being_checked = False
    bot.last_check = timezone.localtime()
    if bot.warnings >= 10:
        try:
            delete_from_elastic(bot.id)
            bot.is_active = False
        except Exception as e:
            print(e)
            print("can not delete from elastic")
    bot.save(update_fields=['is_active', 'is_being_checked', 'warnings', 'all_warnings', 'last_check'])
    session.is_parsing = False
    session.last_parsing = timezone.localtime()
    session.save(update_fields=['is_parsing', 'last_parsing'])


# TODO refactoring
def get_chat(bot, session, client):
    try:
        tg_chat = client.get_entity(bot.username.replace('@', ''))
    except ValueError as e:
        status_bot_founded(bot)
        print(str(e) + str(bot.id) + 'deactive')
        disconnect(bot, session, client)
        return
    except AuthKeyUnregisteredError as e:
        status_bot_founded(bot)
        print(str(e) + str(bot.id) + 'deactive')
        disconnect(bot, session, client)
        return
    except UsernameInvalidError as e:
        status_bot_founded(bot)
        print(str(e) + str(bot.id) + 'deactive')
        disconnect(bot, session, client)
        return
    except telethon.errors.rpcerrorlist.FloodWaitError as f:
        stop_parsing_bot(bot)
        print('telethon' + str(f))
        ban_session(session, f.seconds)
        return
    except Exception as e:
        stop_parsing_bot(bot)
        disconnect(bot, session, client)
        return
    return tg_chat
