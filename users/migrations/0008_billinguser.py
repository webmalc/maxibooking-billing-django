# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-20 08:43
from __future__ import unicode_literals

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
        ('users', '0007_auto_20181120_0743'),
    ]

    operations = [
        migrations.CreateModel(
            name='BillingUser',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
