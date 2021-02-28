from django.db import models


class BotApi(models.Model):
    api_id = models.CharField(max_length=256)
    api_hash = models.CharField(max_length=256)

    def __str__(self):
        return str(self.api_id)


class Sessions(models.Model):
    session = models.FileField(upload_to='', null=True, blank=True)
    name = models.CharField(max_length=256)
    is_active = models.IntegerField(default=1, db_index=True)
    is_parsing = models.BooleanField(default=False)
    start_parsing = models.DateTimeField(null=True, blank=True)
    last_parsing = models.DateTimeField(null=True, blank=True)
    banned_until = models.DateTimeField(null=True, blank=True)
    # proxy_id = models.IntegerField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    bot_api = models.ForeignKey(BotApi, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)

