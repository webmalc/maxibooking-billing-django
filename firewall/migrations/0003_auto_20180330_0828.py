# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-30 08:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firewall', '0002_auto_20180330_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='entries',
            field=models.TextField(db_index=True, help_text='one ip, ip address range or domain per line. Example: 127.0.0.0/24', verbose_name='ip/domain list'),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='entries',
            field=models.TextField(db_index=True, help_text='one ip, ip address range or domain per line. Example: 127.0.0.0/24', verbose_name='ip/domain list'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True, verbose_name='name'),
        ),
    ]
