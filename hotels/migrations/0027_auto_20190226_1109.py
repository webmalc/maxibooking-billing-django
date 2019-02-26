# Generated by Django 2.1.7 on 2019-02-26 11:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotels', '0026_auto_20190212_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='country',
            name='name_en',
            field=models.CharField(db_index=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='country',
            name='name_ru',
            field=models.CharField(db_index=True, max_length=200, null=True),
        ),
    ]
