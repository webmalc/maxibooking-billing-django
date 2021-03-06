# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-07-16 08:01
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clients', '0066_auto_20180712_0859'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='clientru',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='companyworld',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, default=datetime.datetime(2018, 7, 16, 8, 1, 13, 179000, tzinfo=utc), verbose_name='created'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companyworld',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_companyworld_created_by', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AddField(
            model_name='companyworld',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified'),
        ),
        migrations.AddField(
            model_name='companyworld',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_companyworld_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
    ]
