# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-17 16:56
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0004_auto_20170717_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='address',
            field=models.TextField(blank=True, db_index=True, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='address'),
        ),
        migrations.AlterField(
            model_name='property',
            name='description',
            field=models.TextField(blank=True, db_index=True, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='property',
            name='name',
            field=models.CharField(db_index=True, max_length=255, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='name'),
        ),
    ]
