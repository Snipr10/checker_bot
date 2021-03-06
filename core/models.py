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


class UserTg(models.Model):
    user_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    username = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_ban = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    language = models.CharField(max_length=150, default="ru")

    # def __str__(self):
    #     return {"user_id": self.user_id,
    #            "first_name": self.first_name,
    #            "last_name": self.last_name,
    #            "username": self.username
    #            }
    def __str__(self):
        return str(self.user_id)


class Bot(models.Model):
    username = models.CharField(max_length=150, unique=True, blank=True)
    first_name_en = models.CharField(max_length=150, null=True, blank=True)
    first_name_ru = models.CharField(max_length=150, null=True, blank=True)
    last_name_en = models.CharField(max_length=150, null=True, blank=True)
    last_name_ru = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=150)
    is_user = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_ban = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_reply = models.BooleanField(default=False)
    ready_to_use = models.BooleanField(default=False)
    last_check = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    tags = models.CharField(max_length=4000)
    # maybe change max_length and create new table for description
    description_ru = models.CharField(max_length=4000, null=True, blank=True)
    description_en = models.CharField(max_length=4000, null=True, blank=True)
    user = models.ForeignKey(UserTg, on_delete=models.CASCADE, null=True, blank=True)

    all_warnings = models.IntegerField(default=0)
    # if bot active warnings = 0
    warnings = models.IntegerField(default=0)
    is_founded = models.BooleanField(default=True)
    is_being_checked = models.BooleanField(default=False)

    def __str__(self):
        return str(self.username)
