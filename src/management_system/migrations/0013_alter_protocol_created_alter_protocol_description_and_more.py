# Generated by Django 4.2.1 on 2023-05-18 14:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_alter_employee_user_department_and_more"),
        ("management_system", "0012_protocolitem_item_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="protocol",
            name="created",
            field=models.DateField(auto_now_add=True, verbose_name="Data utworzenia"),
        ),
        migrations.AlterField(
            model_name="protocol",
            name="description",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Opis"
            ),
        ),
        migrations.AlterField(
            model_name="protocol",
            name="employee",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="users.employee",
                verbose_name="Pracownik",
            ),
        ),
        migrations.AlterField(
            model_name="protocol",
            name="is_return",
            field=models.BooleanField(blank=True, verbose_name="Czy to zwrot?"),
        ),
        migrations.AlterField(
            model_name="protocol",
            name="modified",
            field=models.DateField(
                auto_now=True, null=True, verbose_name="Data modyfikacji"
            ),
        ),
    ]
