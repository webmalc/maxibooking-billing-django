# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-17 09:08
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import finances.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_auto_20181213_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='code',
            field=models.CharField(blank=True, help_text='The unique user`s code', max_length=20, unique=True, validators=[django.core.validators.MinLengthValidator(3), finances.validators.validate_code]),
        ),
    ]
