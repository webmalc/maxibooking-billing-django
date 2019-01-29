# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-01-29 09:26
from __future__ import unicode_literals

from django.db import migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0022_city_timezone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(blank=True, default='UTC', null=True),
        ),
    ]
