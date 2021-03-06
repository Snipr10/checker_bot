# Generated by Django 3.1.4 on 2021-02-28 10:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BotApi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.CharField(max_length=256)),
                ('api_hash', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='Sessions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session', models.FileField(blank=True, null=True, upload_to='')),
                ('name', models.CharField(max_length=256)),
                ('is_active', models.IntegerField(db_index=True, default=1)),
                ('is_parsing', models.BooleanField(default=False)),
                ('start_parsing', models.DateTimeField(blank=True, null=True)),
                ('last_parsing', models.DateTimeField(blank=True, null=True)),
                ('banned_until', models.DateTimeField(blank=True, null=True)),
                ('proxy_id', models.IntegerField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('bot_api', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.botapi')),
            ],
        ),
    ]
