# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-15 07:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0020_country_is_former'),
        ('users', '0005_auto_20181113_0940'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hotels.Country', verbose_name='country'),
        ),
    ]
