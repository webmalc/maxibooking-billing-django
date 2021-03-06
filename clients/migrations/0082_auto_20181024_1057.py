# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-24 10:57
from __future__ import unicode_literals

import clients.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0081_auto_20181023_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='login_alias',
            field=models.CharField(blank=True, db_index=True, error_messages={'unique': 'Client with this domain already exist.'}, max_length=50, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(4), django.core.validators.RegexValidator(code='invalid_login', message='Enter a valid domain. This value may contain only lowercase letters, numbers, and "-" character.', regex='^[a-z0-9\\-]*$'), clients.validators.validate_client_login_restrictions], verbose_name='login alias'),
        ),
        migrations.AlterUniqueTogether(
            name='client',
            unique_together=set([('login', 'login_alias')]),
        ),
    ]
