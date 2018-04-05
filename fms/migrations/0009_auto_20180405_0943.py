# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-05 09:43
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fms', '0008_auto_20171023_1019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fms',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fms_fms_created_by', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='fms',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fms_fms_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
        migrations.AlterField(
            model_name='kpp',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fms_kpp_created_by', to=settings.AUTH_USER_MODEL, verbose_name='created by'),
        ),
        migrations.AlterField(
            model_name='kpp',
            name='modified_by',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='fms_kpp_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='modified by'),
        ),
    ]
