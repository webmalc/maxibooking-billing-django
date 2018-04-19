# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-04-05 11:38
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('clients', '0050_auto_20180405_0943'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('text', models.TextField(db_index=True, validators=[django.core.validators.MinLengthValidator(2)], verbose_name='text')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='clients.Client', verbose_name='client')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_comment_created_by', to=settings.AUTH_USER_MODEL, verbose_name='created by')),
                ('modified_by', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='clients_comment_modified_by', to=settings.AUTH_USER_MODEL, verbose_name='modified by')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]