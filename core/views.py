from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import asyncio
import random
import time
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta

from django.db.models import Q
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from telethon import TelegramClient, events, sync
from telethon.errors import FloodWaitError
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest

from core.models import Sessions, BotApi


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def add_session(request):
    phone = request.query_params.get('phone')
    bot_id = request.query_params.get('bot_id')
    bot_api = BotApi.objects.get(id=bot_id)
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
    # 25 sleep time
    Sessions.objects.create(name=phone, bot_api_id=bot_api.id,
                            last_parsing=(timezone.now()) + timedelta(minutes=25),
                            created=(timezone.localtime()))

    return Response({'success': 'OK'}, status=status.HTTP_200_OK)
# Create your views here.
