# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-23 10:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fms', '0007_auto_20171020_1035'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fms',
            options={'ordering': ['internal_id'], 'verbose_name_plural': 'fms'},
        ),
        migrations.AlterModelOptions(
            name='kpp',
            options={'ordering': ['internal_id'], 'verbose_name_plural': 'kpp'},
        ),
    ]
