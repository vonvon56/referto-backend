# Generated by Django 5.0.7 on 2024-07-26 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignments', '0002_assignment_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='name',
            field=models.CharField(default='과제 이름', max_length=255),
        ),
    ]
