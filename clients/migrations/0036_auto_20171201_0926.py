# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-01 09:26
from __future__ import unicode_literals

import re

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0035_auto_20171130_1421'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientRu',
            fields=[
                ('passport_serial', models.CharField(
                    db_index=True,
                    max_length=4,
                    validators=[
                        django.core.validators.MinLengthValidator(4),
                        django.core.validators.MaxLengthValidator(4),
                        django.core.validators.RegexValidator(
                            re.compile('^-?\\d+\\Z', 32),
                            code='invalid',
                            message='Enter a valid integer.')
                    ],
                    verbose_name='passport serial')),
                ('passport_number', models.CharField(
                    db_index=True,
                    max_length=6,
                    validators=[
                        django.core.validators.MinLengthValidator(6),
                        django.core.validators.MaxLengthValidator(6),
                        django.core.validators.RegexValidator(
                            re.compile('^-?\\d+\\Z', 32),
                            code='invalid',
                            message='Enter a valid integer.')
                    ],
                    verbose_name='passport number')),
                ('passport_date',
                 models.DateTimeField(verbose_name='passport date')),
                ('passport_issued_by', models.CharField(
                    db_index=True,
                    max_length=255,
                    validators=[django.core.validators.MinLengthValidator(4)],
                    verbose_name='passport issued by')),
                ('inn', models.CharField(
                    db_index=True,
                    max_length=13,
                    validators=[
                        django.core.validators.MinLengthValidator(10),
                        django.core.validators.MaxLengthValidator(13),
                        django.core.validators.RegexValidator(
                            re.compile('^-?\\d+\\Z', 32),
                            code='invalid',
                            message='Enter a valid integer.')
                    ],
                    verbose_name='inn')),
                ('client', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    primary_key=True,
                    related_name='ru',
                    serialize=False,
                    to='clients.Client')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='companyru',
            name='bik',
            field=models.CharField(
                db_index=True,
                max_length=30,
                validators=[django.core.validators.MinLengthValidator(7)],
                verbose_name='bik'),
        ),
        migrations.AlterField(
            model_name='companyru',
            name='inn',
            field=models.CharField(
                db_index=True,
                max_length=13,
                validators=[
                    django.core.validators.MinLengthValidator(10),
                    django.core.validators.MaxLengthValidator(13)
                ],
                verbose_name='inn'),
        ),
    ]
