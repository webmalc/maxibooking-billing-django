# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-17 11:51
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0088_auto_20181129_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='manager_code',
            field=models.CharField(blank=True, max_length=50, null=True, validators=[django.core.validators.MinLengthValidator(3)]),
        ),
    ]
