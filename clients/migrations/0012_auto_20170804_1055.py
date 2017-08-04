# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-04 10:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0011_auto_20170802_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientservice',
            name='begin',
            field=models.DateTimeField(blank=True, db_index=True, verbose_name='begin date'),
        ),
        migrations.AlterField(
            model_name='clientservice',
            name='end',
            field=models.DateTimeField(blank=True, db_index=True, verbose_name='end date'),
        ),
    ]
