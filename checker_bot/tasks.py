import time

from checker_bot.celery.celery import app

from checker_bot.bot import get_bot
from checker_bot.telegram_account_utils import get_client, get_chat, disconnect_success, disconnect_bad


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

