# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-12-15 11:12
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0034_auto_20171215_0931'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicecategory',
            options={'verbose_name_plural': 'service categories'},
        ),
    ]