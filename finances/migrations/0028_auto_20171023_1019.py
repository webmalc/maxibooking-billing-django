# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-23 10:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0027_auto_20170927_1343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'new'), ('processing', 'processing'), ('paid', 'paid'), ('canceled', 'canceled'), ('corrupted', 'corrupted')], db_index=True, default='new', max_length=20, verbose_name='status'),
        ),
    ]
