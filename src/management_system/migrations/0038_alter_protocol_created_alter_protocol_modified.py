# Generated by Django 4.2.1 on 2024-05-15 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management_system", "0037_alter_protocol_modified"),
    ]

    operations = [
        migrations.AlterField(
            model_name="protocol",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Data utworzenia"
            ),
        ),
        migrations.AlterField(
            model_name="protocol",
            name="modified",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="Data modyfikacji"
            ),
        ),
    ]