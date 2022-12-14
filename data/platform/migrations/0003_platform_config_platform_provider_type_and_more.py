# Generated by Django 4.1.2 on 2022-11-06 01:12

from django.db import migrations, models
import systems.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('platform', '0002_platform_environment'),
    ]

    operations = [
        migrations.AddField(
            model_name='platform',
            name='config',
            field=systems.models.fields.DictionaryField(default=dict),
        ),
        migrations.AddField(
            model_name='platform',
            name='provider_type',
            field=models.CharField(default='base', max_length=128),
        ),
        migrations.AddField(
            model_name='platform',
            name='secrets',
            field=systems.models.fields.EncryptedDataField(default={}),
        ),
        migrations.AddField(
            model_name='platform',
            name='variables',
            field=systems.models.fields.DictionaryField(default=dict, editable=False),
        ),
    ]
