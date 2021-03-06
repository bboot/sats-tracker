# Generated by Django 3.2.9 on 2021-11-25 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0003_txout_txins'),
    ]

    operations = [
        migrations.AddField(
            model_name='txout',
            name='amount',
            field=models.BigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='txout',
            name='spent',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='txout',
            name='notes',
            field=models.TextField(default=''),
        ),
    ]
