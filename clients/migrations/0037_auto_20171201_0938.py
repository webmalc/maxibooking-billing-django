# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-01 09:38
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0036_auto_20171201_0926'),
    ]

    operations = [
        migrations.AlterField(
            model_name='companyru',
            name='bik',
            field=models.CharField(db_index=True, max_length=30, validators=[django.core.validators.MinLengthValidator(7), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='bik'),
        ),
        migrations.AlterField(
            model_name='companyru',
            name='corr_account',
            field=models.CharField(max_length=30, validators=[django.core.validators.MinLengthValidator(20), django.core.validators.MaxLengthValidator(30), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='correspondent account'),
        ),
        migrations.AlterField(
            model_name='companyru',
            name='inn',
            field=models.CharField(db_index=True, max_length=13, validators=[django.core.validators.MinLengthValidator(10), django.core.validators.MaxLengthValidator(13), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='inn'),
        ),
        migrations.AlterField(
            model_name='companyru',
            name='kpp',
            field=models.CharField(db_index=True, max_length=9, validators=[django.core.validators.MinLengthValidator(9), django.core.validators.MaxLengthValidator(9), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='kpp'),
        ),
        migrations.AlterField(
            model_name='companyru',
            name='ogrn',
            field=models.CharField(db_index=True, max_length=13, validators=[django.core.validators.MinLengthValidator(13), django.core.validators.MaxLengthValidator(13), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='ogrn'),
        ),
        migrations.AlterField(
            model_name='companyru',
            name='proxy_number',
            field=models.CharField(max_length=50, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='proxy number'),
        ),
        migrations.AlterField(
            model_name='companyworld',
            name='swift',
            field=models.CharField(db_index=True, max_length=20, validators=[django.core.validators.MinLengthValidator(8), django.core.validators.RegexValidator(re.compile('^-?\\d+\\Z', 32), code='invalid', message='Enter a valid integer.')], verbose_name='swift'),
        ),
    ]
