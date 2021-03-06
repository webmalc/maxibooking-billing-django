# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-11 12:25
from __future__ import unicode_literals

from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0066_auto_20190211_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('CAD', 'Canadian Dollar'), ('EUR', 'Euro'), ('RUB', 'Russian Ruble'), ('USD', 'US Dollar')], default='EUR', editable=False, max_length=3),
        ),
    ]
