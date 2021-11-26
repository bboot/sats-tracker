# Generated by Django 3.2.9 on 2021-11-25 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0006_alter_txout_txins'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actor',
            name='notes',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='actor',
            name='txouts',
            field=models.ManyToManyField(blank=True, to='txouts.TxOut'),
        ),
        migrations.AlterField(
            model_name='txout',
            name='notes',
            field=models.TextField(null=True),
        ),
    ]
