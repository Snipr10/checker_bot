from core.models import Bot


# TODO add time (last_check one day and ex)
def get_bot():
    bots = Bot.objects.filter(is_founded=True, is_being_checked=False, last_check__isnull=True)
    if not bots.exists():
        bots = Bot.objects.filter(is_founded=True, is_being_checked=False).order_by('-last_check')

    return bots.first()