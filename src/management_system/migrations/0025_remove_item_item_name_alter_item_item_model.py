# Generated by Django 4.2.1 on 2023-05-25 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management_system", "0024_item_item_model_item_item_producent_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="item",
            name="item_name",
        ),
        migrations.AlterField(
            model_name="item",
            name="item_model",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Model"
            ),
        ),
    ]
