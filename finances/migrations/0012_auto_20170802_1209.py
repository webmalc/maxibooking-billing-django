# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-02 12:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0011_auto_20170802_1206'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('type', 'period', 'period_units', 'is_enabled'), ('title', 'is_enabled')]),
        ),
    ]
