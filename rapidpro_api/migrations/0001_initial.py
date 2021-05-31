# Generated by Django 3.1.2 on 2021-05-29 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TurnRapidproConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=255)),
                ('rp_url', models.URLField()),
                ('rp_api_token', models.CharField(max_length=255)),
                ('turn_url', models.URLField(blank=True)),
                ('turn_api_token', models.CharField(blank=True, max_length=1000)),
                ('hmac_secret', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]
