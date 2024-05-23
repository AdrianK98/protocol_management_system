from rest_framework import serializers
from management_system.models import Item, Protocol, ItemCategory
from users.models import Employee

class ItemCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ItemCategory
        fields = (
            "category_name",
        )


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
    category = ItemCategorySerializer(read_only=True)
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
            "category",
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