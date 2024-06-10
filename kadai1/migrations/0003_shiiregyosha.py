# Generated by Django 5.0.6 on 2024-05-31 02:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kadai1', '0002_remove_employee_id_alter_employee_empid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shiiregyosha',
            fields=[
                ('shiireid', models.CharField(max_length=8, primary_key=True, serialize=False, verbose_name='仕入れ先ID')),
                ('shiiremei', models.CharField(max_length=64, verbose_name='仕入れ先名')),
                ('shiireaddress', models.CharField(max_length=64, verbose_name='仕入れ先住所')),
                ('shiiretel', models.CharField(max_length=13, verbose_name='仕入れ先電話番号')),
                ('shihonkin', models.IntegerField(verbose_name='資本金')),
                ('nouki', models.IntegerField(verbose_name='納期')),
            ],
        ),
    ]