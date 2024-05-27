# Generated by Django 4.2.13 on 2024-05-25 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("management_system", "0044_rename_region_regioncontent"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="userregion",
            name="function",
        ),
        migrations.AddField(
            model_name="userregion",
            name="region",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "Południowy"), (2, "Północny")], null=True
            ),
        ),
        migrations.AlterField(
            model_name="regioncontent",
            name="name",
            field=models.CharField(
                choices=[("południowy", "Południowy"), ("północny", "Północny")],
                max_length=10,
            ),
        ),
    ]