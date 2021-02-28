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

from checker_bot.bot import get_bot
from checker_bot.telegram_account_utils import add_user, get_session, get_client, get_chat, disconnect, \
    disconnect_success, disconnect_bad
from core.models import Sessions, BotApi


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def add_session(request):
    phone = request.query_params.get('phone')
    bot_id = request.query_params.get('bot_id')
    bot_api = BotApi.objects.get(id=bot_id)
    add_user(phone, bot_api)
    return Response({'success': 'OK'}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test_bot(request):
    client, session = get_client()
    if client is None:
        return Response({'not active session'}, status=status.HTTP_200_OK)
    bot = get_bot()
    if bot is None:
        return Response({'not active bot'}, status=status.HTTP_200_OK)
    chat = get_chat(bot, session, client)
    if chat is None:
        return Response({'not active chat'}, status=status.HTTP_200_OK)
    client.send_message(chat, '/start')
    time.sleep(10)
    client.get_messages(chat, limit=1)
    if client.get_messages(chat, limit=1)[0].sender.username == bot.username:
        disconnect_success(bot, session)
        return Response({'success': 'OK'}, status=status.HTTP_200_OK)
    else:
        disconnect_bad(bot, session)
        return Response({'success': 'Not Ok'}, status=status.HTTP_200_OK)

