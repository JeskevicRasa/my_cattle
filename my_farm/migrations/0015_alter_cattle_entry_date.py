# Generated by Django 4.2 on 2023-07-12 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_farm', '0014_alter_cattle_birth_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cattle',
            name='entry_date',
            field=models.DateField(blank=True),
        ),
    ]
