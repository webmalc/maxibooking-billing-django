# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-16 08:01
from __future__ import unicode_literals

from django.db import migrations, models


def set_id(apps, schema_editor):
    CompanyWorld = apps.get_model('clients', 'CompanyWorld')
    for i, entry in enumerate(CompanyWorld.objects.all()):
        if not entry.id:
            entry.id = i + 1
            entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0067_auto_20180716_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyworld',
            name='id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunPython(set_id),
    ]