# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-28 12:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0032_auto_20171128_0843'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='companyru',
            options={'verbose_name': 'ru', 'verbose_name_plural': 'ru'},
        ),
        migrations.AlterModelOptions(
            name='companyworld',
            options={'verbose_name': 'world', 'verbose_name_plural': 'world'},
        ),
        migrations.AlterField(
            model_name='companyru',
            name='form',
            field=models.CharField(choices=[('ooo', 'ooo'), ('oao', 'oao'), ('ip', 'ip'), ('zao', 'zao')], db_index=True, max_length=20, verbose_name='form'),
        ),
    ]
