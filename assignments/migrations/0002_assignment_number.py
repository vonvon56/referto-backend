# Generated by Django 5.0.7 on 2024-07-23 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assignment',
            name='number',
            field=models.PositiveIntegerField(editable=False, null=True),
        ),
    ]
