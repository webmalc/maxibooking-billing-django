# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-28 12:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0085_auto_20181128_0827'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ['-created'], 'permissions': (('change_own', 'Can change only own entries'), ('change_department', 'Can change only department entries'))},
        ),
    ]