# Generated by Django 4.2.1 on 2023-05-18 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_rename_diagworkers_employee"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="user_name",
            field=models.CharField(max_length=200, verbose_name="Imię Pracownika"),
        ),
    ]
