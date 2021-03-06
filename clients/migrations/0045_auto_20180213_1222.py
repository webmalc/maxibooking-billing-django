# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-02-13 12:22
from __future__ import unicode_literals

import clients.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0044_auto_20180201_0751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='login',
            field=models.CharField(db_index=True, error_messages={'unique': 'Client with this domain already exist.'}, max_length=50, unique=True, validators=[django.core.validators.MinLengthValidator(4), django.core.validators.RegexValidator(code='invalid_login', message='Enter a valid domain. This value may contain only lowercase letters, numbers, and "-" character.', regex='^[a-z0-9\\-]*$'), clients.validators.validate_client_login_restrictions], verbose_name='login'),
        ),
    ]
