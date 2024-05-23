# Generated by Django 4.2.1 on 2024-05-23 18:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0006_alter_employee_user_email_alter_employee_user_login"),
        ("management_system", "0039_item_created"),
    ]

    operations = [
        migrations.AlterField(
            model_name="item",
            name="item_user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="item_user",
                to="users.employee",
                verbose_name="Pracownik",
            ),
        ),
    ]
