# Generated by Django 4.2 on 2023-07-16 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('my_farm', '0021_field_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='herd',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='field_herds', to='my_farm.field'),
        ),
    ]
