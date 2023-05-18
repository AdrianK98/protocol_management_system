from rest_framework import serializers
from .models import Item
from users.models import Employee


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            "id",
            "item_name",
            "item_sn",
            "item_it",
            "item_kk",
        )

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = (
            "id",
            "user_name",
            "user_surname",
            "user_department",
            "user_location",
        )