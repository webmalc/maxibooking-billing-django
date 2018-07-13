# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-12 08:52
from __future__ import unicode_literals

from django.db import migrations, models


def set_id(apps, schema_editor):
    ClientRu = apps.get_model('clients', 'ClientRu')
    for i, ru in enumerate(ClientRu.objects.all()):
        ru.id = i + 1
        ru.save()


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0063_auto_20180711_0945'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientwebsite',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='clientru',
            name='id',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunPython(set_id),
    ]
