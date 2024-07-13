# Generated by Django 5.0.1 on 2024-07-12 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paperinfos', '0004_remove_paperinfo_reference_paperinfo_apa_reference_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paperinfo',
            name='apa_reference',
        ),
        migrations.RemoveField(
            model_name='paperinfo',
            name='chicago_reference',
        ),
        migrations.RemoveField(
            model_name='paperinfo',
            name='mla_reference',
        ),
        migrations.RemoveField(
            model_name='paperinfo',
            name='vancouver_reference',
        ),
        migrations.AddField(
            model_name='paperinfo',
            name='reference',
            field=models.TextField(blank=True, null=True),
        ),
    ]
