# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-01-22 07:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0041_auto_20180115_1314'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientservice',
            name='is_paid',
            field=models.BooleanField(db_index=True, default=False, verbose_name='is paid'),
        ),
    ]
