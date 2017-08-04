# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-04 08:10
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0008_auto_20170731_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='rooms',
            field=models.PositiveIntegerField(db_index=True, default=1, help_text='max rooms', validators=[django.core.validators.MinValueValidator(1)], verbose_name='rooms'),
            preserve_default=False,
        ),
    ]
