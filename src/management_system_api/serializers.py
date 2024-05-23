from rest_framework import serializers
from management_system.models import Item, Protocol
from users.models import Employee

class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Employee
        fields = (
            "id",
            "user_name",
            "user_surname",
            "user_department",
            "user_location",
        )


class ItemSerializer(serializers.HyperlinkedModelSerializer):
    item_user = EmployeeSerializer(read_only=True)
    class Meta:
        model = Item
        fields = (
            "id",
            "item_sn",
            "item_it",
            "item_kk",
            "item_user",
            "created",
            "item_model",
        )


class ProtocolSerializer(serializers.HyperlinkedModelSerializer):
    employee = EmployeeSerializer(read_only=True)
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