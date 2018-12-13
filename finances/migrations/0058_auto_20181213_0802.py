# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-13 08:02
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0057_auto_20181212_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='percentage_discount',
            field=models.FloatField(db_index=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='percentage discount'),
        ),
    ]