# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-08-14 08:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0050_subscription'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subscriptions', to='finances.Order', verbose_name='order'),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_system',
            field=models.CharField(blank=True, choices=[('stripe', 'stripe'), ('braintree', 'braintree'), ('braintree-subscription', 'braintree-subscription'), ('rbk', 'rbk'), ('sberbank', 'sberbank'), ('bill', 'bill')], db_index=True, max_length=30, null=True, verbose_name='payment system'),
        ),
    ]
