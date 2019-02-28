# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2019-02-11 12:03
from __future__ import unicode_literals

from decimal import Decimal
from django.db import migrations
import djmoney.models.fields
import djmoney.models.validators


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0090_client_managers_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clientservice',
            name='price',
            field=djmoney.models.fields.MoneyField(blank=True, db_index=True, decimal_places=2, default=Decimal('0.0'), max_digits=20, validators=[djmoney.models.validators.MinMoneyValidator(0)], verbose_name='price'),
        ),
    ]