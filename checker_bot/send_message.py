import requests

from checker_bot.settings import SUPPORT_USER_URL


def send_message(user, text):
    try:
        post_data = {
            "user_id": user.pk,
            "text": text
        }
        response = requests.post(SUPPORT_USER_URL, json=post_data)
        if response.status_code != 200:
            print(response.text)
    except Exception as e:
        print(e)