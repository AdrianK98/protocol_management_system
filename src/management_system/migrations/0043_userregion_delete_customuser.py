# Generated by Django 4.2.13 on 2024-05-25 12:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("management_system", "0042_customuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserRegion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "function",
                    models.PositiveSmallIntegerField(
                        choices=[
                            (1, "Assistant DAO"),
                            (2, "Chef Service Etude"),
                            (3, "Chef Departement Etude"),
                            (4, "Directeur Generale"),
                            (5, "admin"),
                            (6, "Coordinateur des Operations"),
                            (7, "Conducteurs des Travaux"),
                            (8, "Chef de Projet"),
                            (9, "DEGP"),
                            (10, "Magasinier"),
                            (11, "Intervenant"),
                        ],
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="CustomUser",
        ),
    ]
