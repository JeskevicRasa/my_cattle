# Generated by Django 4.2 on 2023-07-18 07:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_farm', '0021_cattle_herd_field_is_active_field_picture_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cattle',
            name='herd',
        ),
        migrations.AddField(
            model_name='cattle',
            name='herd',
            field=models.ManyToManyField(blank=True, related_name='cattle', to='my_farm.herd'),
        ),
    ]