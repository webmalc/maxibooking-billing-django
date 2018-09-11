# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-09-11 10:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0075_auto_20180815_1247'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='source',
            field=models.CharField(choices=[('chat', 'chat'), ('phone', 'phone'), ('cold call', 'cold call'), ('email', 'email'), ('registration', 'registration')], db_index=True, default='registration', max_length=20, verbose_name='source'),
        ),
    ]
