# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-27 14:05
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0028_company'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='company',
            options={'ordering': ['-created'], 'verbose_name_plural': 'companies'},
        ),
        migrations.AlterField(
            model_name='company',
            name='account_number',
            field=models.CharField(db_index=True, max_length=50, validators=[django.core.validators.MinLengthValidator(10)]),
        ),
        migrations.AlterField(
            model_name='company',
            name='bik',
            field=models.CharField(blank=True, db_index=True, max_length=20, null=True, validators=[django.core.validators.MinLengthValidator(7)], verbose_name='bik'),
        ),
        migrations.AlterField(
            model_name='company',
            name='postal_code',
            field=models.CharField(db_index=True, max_length=50, validators=[django.core.validators.MinLengthValidator(2)]),
        ),
        migrations.AlterField(
            model_name='company',
            name='proxy_number',
            field=models.CharField(blank=True, max_length=50, null=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='proxy number'),
        ),
        migrations.AlterField(
            model_name='company',
            name='swift',
            field=models.CharField(db_index=True, max_length=20, validators=[django.core.validators.MinLengthValidator(8)], verbose_name='swift'),
        ),
        migrations.AlterUniqueTogether(
            name='company',
            unique_together=set([('client', 'name')]),
        ),
    ]