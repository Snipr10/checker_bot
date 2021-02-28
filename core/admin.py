from django.contrib import admin

from core.models import BotApi, Sessions, Bot

admin.site.register(BotApi)
admin.site.register(Sessions)
admin.site.register(Bot)

# Register your models here.
