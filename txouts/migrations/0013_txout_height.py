# Generated by Django 3.2.9 on 2021-12-18 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0012_alter_txout_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='txout',
            name='height',
            field=models.IntegerField(default=1),
        ),
    ]
