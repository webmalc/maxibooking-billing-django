# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-10-20 10:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fms', '0006_auto_20171020_0727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fms',
            name='code',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='code'),
        ),
        migrations.AlterField(
            model_name='kpp',
            name='code',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True, verbose_name='code'),
        ),
        migrations.AlterUniqueTogether(
            name='fms',
            unique_together=set([('internal_id', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='kpp',
            unique_together=set([('internal_id', 'name')]),
        ),
    ]