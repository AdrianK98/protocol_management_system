from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from rest_framework import generics
from .serializers import ItemSerializer,EmployeeSerializer
from .forms import EmployeeForm
# Create your views here.
from users.models import Employee
from .models import Item


@login_required
def mainView(request):
    return render(request, "management_system/home.html", {})

@login_required
def showEmployees(request):
    employeeList = Employee.objects.all()
    data={
        "employeeList":employeeList
    }
    return render(request, "management_system/employees.html", data)

@login_required
def newProtocol(request):
    return render(request, "management_system/new_protocol.html", {})

@login_required
def protocolsView(request):
    return render(request, "management_system/protocols.html", {})

@login_required
def addEmployeeView(request):
    form = EmployeeForm(request.POST or None)
    if form.is_valid():
        form.save()
    data={
        "form":form
    }
    return render(request, "management_system/add_new_employee.html", data)
    
@login_required
def itemsView(request):
    itemListQuery = Item.objects.all()
    print(itemListQuery)
    data={
        "itemList":itemListQuery
    }
    return render(request, "management_system/items.html", data)





class ItemList(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class ItemDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

class EmployeeList(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer