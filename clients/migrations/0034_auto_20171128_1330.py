# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-28 13:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0033_auto_20171128_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyru',
            name='company',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='ru', serialize=False, to='clients.Company'),
        ),
        migrations.AlterField(
            model_name='companyworld',
            name='company',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='world', serialize=False, to='clients.Company'),
        ),
    ]