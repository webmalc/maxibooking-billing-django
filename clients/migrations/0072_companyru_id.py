# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-17 08:03
from __future__ import unicode_literals

from django.db import migrations, models


def set_id(apps, schema_editor):
    CompanyRu = apps.get_model('clients', 'CompanyRu')
    for i, entry in enumerate(CompanyRu.objects.all()):
        if not entry.id:
            entry.id = i + 1
            entry.save()


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0071_auto_20180717_0803'),
    ]

    operations = [
        migrations.AddField(
            model_name='companyru',
            name='id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunPython(set_id),
    ]
