from django.shortcuts import render
from management_system.models import Item, Protocol
from users.models import Employee
from rest_framework import generics, permissions, viewsets
from .serializers import ItemSerializer,EmployeeSerializer,ProtocolSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import renderers
from rest_framework.decorators import action
from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from .filtersets import ItemFilter, EmployeeFilter, ProtocolFilter

from rest_framework import filters
# Create your views here.


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [filters.SearchFilter,DjangoFilterBackend,filters.OrderingFilter]
    filterset_class = ItemFilter
    search_fields = ["item_sn","item_it","item_kk",'item_model','item_user__user_surname','category__category_name']
    ordering_fields = '__all__'
    #defualt ordering field
    ordering = ['-id']

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        item = self.get_object()
        return Response(item)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter,DjangoFilterBackend,filters.OrderingFilter]
    filterset_class = EmployeeFilter
    search_fields = ['user_name','user_surname']
    filterset_fields = '__all__'
    ordering_fields = '__all__'
    #defualt ordering field
    ordering = ['-id']



    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        employee = self.get_object()
        return Response(employee)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)



class ProtocolViewSet(viewsets.ModelViewSet):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter,DjangoFilterBackend,filters.OrderingFilter]
    filterset_class = ProtocolFilter
    search_fields = ['barcode']
    filterset_fields = '__all__'
    ordering_fields = '__all__'
    #defualt ordering field
    ordering = ['-id']

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        protocol = self.get_object()
        return Response(protocol)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
