# Generated by Django 5.0.6 on 2024-06-07 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kadai1', '0004_patient'),
    ]

    operations = [
        migrations.CreateModel(
            name='Medicine',
            fields=[
                ('medicineid', models.CharField(max_length=8, primary_key=True, serialize=False, verbose_name='薬剤 ID')),
                ('medicinename', models.CharField(max_length=64, verbose_name='薬剤名')),
                ('unit', models.CharField(max_length=8, verbose_name='単位')),
            ],
        ),
    ]