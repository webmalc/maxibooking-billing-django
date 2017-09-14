# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-11 11:24
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0017_auto_20170911_1118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='price',
            field=models.DecimalField(db_index=True, decimal_places=2, default=0, help_text='Delete to recalculate price', max_digits=20, validators=[django.core.validators.MinValueValidator(0)], verbose_name='price'),
        ),
    ]