# Generated by Django 4.2 on 2023-07-16 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_farm', '0020_cattle_herd'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
