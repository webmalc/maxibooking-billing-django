# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-16 11:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0031_auto_20171109_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='note_en',
            field=models.TextField(blank=True, db_index=True, help_text='Clear to regenerate note', null=True, verbose_name='note'),
        ),
        migrations.AddField(
            model_name='order',
            name='note_ru',
            field=models.TextField(blank=True, db_index=True, help_text='Clear to regenerate note', null=True, verbose_name='note'),
        ),
    ]