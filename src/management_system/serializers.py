from rest_framework import serializers
from .models import Item, Protocol
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

class ProtocolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Protocol
        fields = (
            "id",
            "created",
            "barcode",
            "modified",
            "description",
            "is_return",
            "employee",
        )