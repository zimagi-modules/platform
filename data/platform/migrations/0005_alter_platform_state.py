# Generated by Django 4.1.2 on 2022-11-06 01:53

from django.db import migrations
import systems.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('platform', '0004_platform_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform',
            name='state',
            field=systems.models.fields.EncryptedDataField(default='', editable=False),
        ),
    ]
