# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-18 14:59
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='login',
            field=models.CharField(db_index=True, max_length=50, unique=True, validators=[django.core.validators.MinLengthValidator(4)]),
        ),
    ]
