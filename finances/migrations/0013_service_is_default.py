# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-03 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0012_auto_20170802_1209'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='is_default',
            field=models.BooleanField(db_index=True, default=False, verbose_name='is default'),
        ),
    ]
