# Generated by Django 3.2.9 on 2021-11-25 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='actor',
            old_name='address',
            new_name='txouts',
        ),
        migrations.AddField(
            model_name='txout',
            name='actors',
            field=models.ManyToManyField(to='txouts.Actor'),
        ),
    ]
