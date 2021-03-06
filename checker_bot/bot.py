from core.models import Bot
from django.utils import timezone
from datetime import timedelta


# TODO add time (last_check one day and ex)
def get_bot():
    bots = Bot.objects.filter(is_founded=True, is_being_checked=False, ready_to_use=False)
    if not bots.exists():
        bots = Bot.objects.filter(is_founded=True, is_being_checked=False, last_check__isnull=True)
        if not bots.exists():
            bots = Bot.objects.filter(is_founded=True, is_being_checked=False,
                                      last_check__gte=timezone.now() + timedelta(days=1)).order_by('-last_check')
    return bots.first()
