# Generated by Django 3.2.9 on 2021-11-27 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0009_auto_20211125_2055'),
    ]

    operations = [
        migrations.AddField(
            model_name='txout',
            name='owned',
            field=models.BooleanField(default=True),
        ),
    ]
