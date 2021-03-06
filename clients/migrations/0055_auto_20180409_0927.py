# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-09 09:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0054_client_refusal_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='type',
            field=models.CharField(choices=[('message', 'message'), ('refusal', 'refusal')], db_index=True, default='message', max_length=20, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='client',
            name='refusal_reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients', to='clients.RefusalReason', verbose_name='refusal reason'),
        ),
    ]
