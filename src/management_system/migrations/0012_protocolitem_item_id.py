# Generated by Django 4.2.1 on 2023-05-18 13:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("management_system", "0011_remove_protocolitem_employee_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="protocolitem",
            name="item_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="management_system.item",
            ),
        ),
    ]
