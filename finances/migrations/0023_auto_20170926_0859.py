# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-26 08:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0022_auto_20170913_1447'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ('-modified', '-created')},
        ),
        migrations.AddField(
            model_name='order',
            name='disable_date',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='disable date'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('new', 'new'), ('processing', 'processing'), ('paid', 'paid'), ('canceled', 'canceled')], db_index=True, default='new', max_length=20, verbose_name='status'),
        ),
    ]
