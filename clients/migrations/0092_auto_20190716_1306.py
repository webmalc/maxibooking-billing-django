# Generated by Django 2.1.7 on 2019-07-16 13:06

import clients.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0091_auto_20190211_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='clientwebsite',
            name='own_domain_name',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Does the website use its own domain name?'),
        ),
        migrations.AlterField(
            model_name='client',
            name='login',
            field=models.CharField(blank=True, db_index=True, error_messages={'unique': 'Client with this domain already exist.'}, max_length=50, unique=True, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator(code='invalid_login', message='Enter a valid domain. This value may contain only lowercase letters, numbers, and "-" character.', regex='^[a-z0-9\\-]*$'), clients.validators.validate_client_login_restrictions], verbose_name='login'),
        ),
        migrations.AlterField(
            model_name='client',
            name='login_alias',
            field=models.CharField(blank=True, db_index=True, error_messages={'unique': 'Client with this domain already exist.'}, max_length=50, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(2), django.core.validators.RegexValidator(code='invalid_login', message='Enter a valid domain. This value may contain only lowercase letters, numbers, and "-" character.', regex='^[a-z0-9\\-]*$'), clients.validators.validate_client_login_restrictions], verbose_name='login alias'),
        ),
        migrations.AlterField(
            model_name='companyworld',
            name='swift',
            field=models.CharField(db_index=True, max_length=20, validators=[django.core.validators.MinLengthValidator(8)], verbose_name='swift'),
        ),
    ]
