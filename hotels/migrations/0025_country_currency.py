# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-12 13:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0024_auto_20190129_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='currency',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
