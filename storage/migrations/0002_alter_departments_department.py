# Generated by Django 5.1.2 on 2024-11-11 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='departments',
            name='department',
            field=models.CharField(max_length=50, verbose_name='Отдел/Цех'),
        ),
    ]
