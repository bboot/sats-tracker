# Generated by Django 3.2.9 on 2021-12-19 18:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0013_txout_height'),
    ]

    operations = [
        migrations.AddField(
            model_name='txout',
            name='data',
            field=models.TextField(blank=True, null=True),
        ),
    ]