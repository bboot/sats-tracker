# Generated by Django 3.2.9 on 2022-01-01 00:18

from django.db import migrations
import encrypted_fields.fields


class Migration(migrations.Migration):

    dependencies = [
        ('txouts', '0018_auto_20211231_2329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='txout',
            name='unique_key',
            field=encrypted_fields.fields.SearchField(blank=True, db_index=True, encrypted_field_name='_unique_key_data', hash_key='f99e1de045c14627fd83463a93a01edbb0a29f1004bf3c60d04fc57fb8ac2d99', max_length=66, null=True, unique=True),
        ),
    ]