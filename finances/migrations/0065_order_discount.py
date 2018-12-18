# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-18 10:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0064_clientdiscount_usage_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='finances.ClientDiscount'),
        ),
    ]
