# Generated by Django 4.2.1 on 2023-07-25 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management_system", "0028_protocol_is_scanned"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="item_model",
            field=models.CharField(max_length=200, verbose_name="Model"),
        ),
        migrations.AlterField(
            model_name="item",
            name="item_producent",
            field=models.CharField(max_length=200, verbose_name="Producent"),
        ),
        migrations.AlterField(
            model_name="item",
            name="item_sn",
            field=models.CharField(max_length=200, verbose_name="Numer S/N"),
        ),
    ]
