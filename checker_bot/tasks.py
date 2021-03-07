import time
from datetime import timedelta

from django.db.models import Q

from checker_bot.add_account_user import add_number
from checker_bot.celery.celery import app

from checker_bot.bot import get_bot
from checker_bot.settings import MIN_USER_COUNT, MIN_USER_DAY
from checker_bot.telegram_account_utils import get_client, get_chat, disconnect_success, disconnect_bad
from core.elastic.elastic import add_to_elastic_bot_data
from core.models import Sessions, BotApi
from django.utils import timezone


@app.task
def start_task_check_bot():
    print('start task')
    client, session = get_client()
    if client is None:
        print('client is None')
        return
    bot = get_bot()
    if bot is None:
        print('bot is None')
        return
    chat = get_chat(bot, session, client)
    if chat is None:
        print('chat is None')
        return
    client.send_message(chat, '/start')
    time.sleep(10)
    if client.get_messages(chat, limit=1)[0].sender.username == bot.username:
        disconnect_success(bot, session)
        print('disconnect_success')
        return
    else:
        disconnect_bad(bot, session)
        print('disconnect_bad')
        return


@app.task
def active_ban_session():
    print('active_ban_session')
    Sessions.objects.filter(banned_until__lte=(timezone.now())).update(
        is_active=1, is_parsing=False, banned_until=None)


@app.task
def add_client():
    now = timezone.localtime() - timedelta(days=1)
    if Sessions.objects.filter(Q(is_active__lte=10) | Q(banned_until__isnull=False)).count() < MIN_USER_COUNT:
        print('Sessions < MIN_USER_COUNT ')

        for bot_api in BotApi.objects.all():
            print('bot_api' + str(bot_api.id))
            count_today_created_sessions = Sessions.objects.filter(Q(is_active__lte=10) | Q(banned_until__isnull=False),
                                                                   bot_api_id=bot_api.id, created__gte=now).count()
            if count_today_created_sessions < MIN_USER_DAY:
                try:
                    while MIN_USER_DAY - count_today_created_sessions > 0:
                        print("start")
                        if MIN_USER_DAY >= Sessions.objects.filter(bot_api_id=bot_api.id, created__gte=now).count():
                            print('bot_api ' + str(bot_api.id) + ' count ' +str(
                                Sessions.objects.filter(Q(is_active__lte=10) | Q(banned_until__isnull=False),
                                                        bot_api_id=bot_api.id, created__gte=now).count()))
                            try:
                                print('client add ' + str(add_number(bot_api)))
                            except Exception as e:
                                print('add_client add' + str(e))
                        count_today_created_sessions = count_today_created_sessions + 1
                except Exception as e:
                    print('add_client ' + str(e))
