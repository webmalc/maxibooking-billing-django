# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-24 13:31
from __future__ import unicode_literals

import annoying.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0023_restrictions'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restrictions',
            name='id',
        ),
        migrations.AlterField(
            model_name='restrictions',
            name='client',
            field=annoying.fields.AutoOneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='restrictions', serialize=False, to='clients.Client'),
        ),
    ]
