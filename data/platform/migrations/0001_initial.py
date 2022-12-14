# Generated by Django 4.1.2 on 2022-11-05 20:12

from django.db import migrations, models
import systems.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('created', models.DateTimeField(editable=False, null=True)),
                ('updated', models.DateTimeField(editable=False, null=True)),
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('reference', models.CharField(default=None, max_length=256, null=True)),
                ('remote', models.CharField(default=None, max_length=256, null=True)),
                ('state', systems.models.fields.EncryptedDataField(default='')),
            ],
            options={
                'verbose_name': 'platform',
                'verbose_name_plural': 'platforms',
                'db_table': 'platform_platform',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
    ]
