# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-06 12:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0005_auto_20181130_1301'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['-created'], 'permissions': (('change_related_comment', 'Can change related comments'), ('change_add_comment', 'Can add related comments'))},
        ),
    ]
