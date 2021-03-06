# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-24 13:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0048_auto_20180423_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_system',
            field=models.CharField(blank=True, choices=[('braintree', 'braintree'), ('braintree-subscription', 'braintree-subscription'), ('rbk', 'rbk'), ('bill', 'bill')], db_index=True, max_length=30, null=True, verbose_name='payment system'),
        ),
        migrations.AlterField(
            model_name='service',
            name='period_units',
            field=models.CharField(choices=[('month', 'month'), ('year', 'year')], db_index=True, default='month', max_length=20, verbose_name='units of period'),
        ),
    ]
