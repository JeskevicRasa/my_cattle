# Generated by Django 4.2 on 2023-07-18 07:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_farm', '0022_remove_cattle_herd_cattle_herd'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cattle',
            name='herd',
        ),
        migrations.AddField(
            model_name='cattle',
            name='herd',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='my_farm.herd'),
        ),
    ]
