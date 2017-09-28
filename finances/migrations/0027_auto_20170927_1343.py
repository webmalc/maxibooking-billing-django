# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-27 13:43
from __future__ import unicode_literals

from decimal import Decimal
import django.core.validators
from django.db import migrations
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0026_auto_20170927_1225'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='price_currency',
            field=djmoney.models.fields.CurrencyField(choices=[('EUR', 'Euro'), ('RUB', 'Russian Ruble')], default='EUR', editable=False, max_length=3),
        ),
        migrations.AlterField(
            model_name='order',
            name='price',
            field=djmoney.models.fields.MoneyField(db_index=True, decimal_places=2, default=Decimal('0'), help_text='Set zero to recalculate price', max_digits=20, validators=[django.core.validators.MinValueValidator(0)], verbose_name='price'),
        ),
        migrations.AlterField(
            model_name='price',
            name='price',
            field=djmoney.models.fields.MoneyField(db_index=True, decimal_places=2, default=Decimal('0.0'), max_digits=20, validators=[django.core.validators.MinValueValidator(0)], verbose_name='price'),
        ),
    ]
