# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-02 14:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0012_auto_20171023_1105'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='region',
            options={'ordering': ['name']},
        ),
        migrations.AlterUniqueTogether(
            name='region',
            unique_together=set([]),
        ),
    ]
