# Generated by Django 5.0.7 on 2024-07-22 15:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('papers', '0003_alter_paper_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paper',
            name='number',
        ),
    ]
