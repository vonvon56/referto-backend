# Generated by Django 5.0.7 on 2024-12-05 08:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('papers', '0005_paper_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('note_id', models.AutoField(primary_key=True, serialize=False)),
                ('content', models.TextField(blank=True)),
                ('highlightAreas', models.JSONField()),
                ('quote', models.TextField(blank=True, null=True)),
                ('paper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='papers.paper')),
            ],
        ),
    ]
