# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-24 15:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0032_auto_20171116_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='default_rooms',
            field=models.PositiveIntegerField(blank=True, db_index=True, null=True, verbose_name='default rooms'),
        ),
    ]