from django_filters import FilterSet, AllValuesFilter, DateTimeFilter, NumberFilter, CharFilter
from management_system.models import Item, Protocol
from users.models import Employee

class ItemFilter(FilterSet):
    item_sn = CharFilter(lookup_expr='icontains')
    item_it = CharFilter(lookup_expr='icontains')
    item_kk = CharFilter(lookup_expr='icontains')
    item_model = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Item
        fields = ['item_sn', 'item_it','item_kk','item_model']

class EmployeeFilter(FilterSet):
    user_name = CharFilter(lookup_expr='icontains')
    user_surname = CharFilter(lookup_expr='icontains')


    class Meta:
        model = Employee
        fields = ['user_name', 'user_surname']

class ProtocolFilter(FilterSet):
    barcode = CharFilter(lookup_expr='icontains')


    class Meta:
        model = Protocol
        fields = ['barcode']

