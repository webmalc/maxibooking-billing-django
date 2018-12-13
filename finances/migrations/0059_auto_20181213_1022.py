# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-13 10:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0058_auto_20181213_0802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discount',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managers', to='users.BillingUser', verbose_name='manager'),
        ),
    ]