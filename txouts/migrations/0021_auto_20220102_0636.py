# Generated by Django 3.2.9 on 2022-01-02 06:36

from django.db import migrations

from encrypted_fields import fields


def move_data(apps, schema_editor):
    TxOut = apps.get_model('txouts', 'TxOut')
    for txout in TxOut.objects.all():
        txout.address = txout.address_temp
        txout.transaction = txout.transaction_temp
        txout.notes = txout.notes_temp
        txout.amount = txout.amount_temp
        txout.height = txout.height_temp
        txout.spent_tx = txout.spent_tx_temp
        txout.data = txout.data_temp
        txout.unique_key = txout.address_temp + ' ' + txout.transaction_temp
        txout.save()


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0020_alter_txout_unique_together'),
    ]

    operations = [
        migrations.RenameField(
            model_name='txout',
            old_name='address',
            new_name='address_temp',
        ),
        migrations.RenameField(
            model_name='txout',
            old_name='transaction',
            new_name='transaction_temp',
        ),
        migrations.RenameField(
            model_name='txout',
            old_name='notes',
            new_name='notes_temp',
        ),
        migrations.RenameField(
            model_name='txout',
            old_name='amount',
            new_name='amount_temp',
        ),
        migrations.RenameField(
            model_name='txout',
            old_name='height',
            new_name='height_temp',
        ),
        migrations.RenameField(
            model_name='txout',
            old_name='spent_tx',
            new_name='spent_tx_temp',
        ),
        migrations.RenameField(
            model_name='txout',
            old_name='data',
            new_name='data_temp',
        ),
        migrations.AddField(
            model_name='txout',
            name='address',
            field=fields.EncryptedCharField(max_length=100, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='txout',
            name='transaction',
            field=fields.EncryptedCharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='txout',
            name='notes',
            field=fields.EncryptedTextField(blank=True),
        ),
        migrations.AddField(
            model_name='txout',
            name='amount',
            field=fields.EncryptedBigIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='txout',
            name='height',
            field=fields.EncryptedIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='txout',
            name='spent_tx',
            field=fields.EncryptedCharField(max_length=100, blank=True),
        ),
        migrations.AddField(
            model_name='txout',
            name='data',
            field=fields.EncryptedTextField(default="{}"),
        ),
        migrations.RunPython(move_data),
        migrations.RemoveField(
            model_name='txout',
            name='address_temp'
        ),
        migrations.RemoveField(
            model_name='txout',
            name='transaction_temp'
        ),
        migrations.RemoveField(
            model_name='txout',
            name='notes_temp'
        ),
        migrations.RemoveField(
            model_name='txout',
            name='amount_temp'
        ),
        migrations.RemoveField(
            model_name='txout',
            name='height_temp'
        ),
        migrations.RemoveField(
            model_name='txout',
            name='spent_tx_temp'
        ),
        migrations.RemoveField(
            model_name='txout',
            name='data_temp'
        ),
    ]