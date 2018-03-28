# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-28 08:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0044_auto_20180326_0901'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='type',
            field=models.CharField(choices=[('rooms', 'rooms'), ('other', 'other')], db_index=True, default='other', max_length=20, verbose_name='type'),
        ),
    ]
