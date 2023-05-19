from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from rest_framework import generics
import json
from .serializers import ItemSerializer,EmployeeSerializer,ProtocolSerializer
from .forms import EmployeeForm, ProtocolForm, ItemForm



# Create your views here.
from users.models import Employee
from .models import Item,Protocol, ProtocolItem



@login_required
def mainView(request):

    return render(request, "management_system/home.html", {})

@login_required
def showEmployees(request):
    employeeList = Employee.objects.all()
    context={
        "employeeList":employeeList
    }
    return render(request, "management_system/employees.html", context)

@login_required
def newProtocol(request):
    protocolForm = ProtocolForm(request.POST or None)
    itemForm = ItemForm(request.POST or None)
    if request.method == 'POST':
            if protocolForm.is_valid() and itemForm.is_valid():
                try:
                    newProtocol = protocolForm.save()
                    newItem = itemForm.save()
                    ProtocolItem(protocol_id=newProtocol,item_id=newItem).save()
                    if 'saveAndEnd' in request.POST:
                        return redirect("home")
                    elif 'saveAndContinue' in request.POST:
                        return redirect("addNextItem",pk=newProtocol.id)
                    
                except:
                    print("An exception occurred")

    context={
            "protocolForm":protocolForm,
            "itemForm":itemForm
        }
    return render(request, "management_system/new_protocol.html", context)

@login_required
def addNextItem(request,pk):
    itemForm = ItemForm(request.POST or None)
    if request.method == 'POST':
            newProtocol = Protocol.objects.get(id=pk)
            if itemForm.is_valid():
                try:
                    newItem = itemForm.save()
                    ProtocolItem(protocol_id=newProtocol,item_id=newItem).save()
                    if 'saveAndEnd' in request.POST:
                        return redirect("home")
                    elif 'saveAndContinue' in request.POST:
                        return redirect("addNextItem",pk=newProtocol.id)
                    
                except:
                    print("An exception occurred")    
    context={
            "itemForm":itemForm
        }
    return render(request, "management_system/new_protocol_next_item.html", context)


@login_required
def protocolsView(request):
    protocolQuery = Protocol.objects.all()
    context={
        "protocolList":protocolQuery
    }
    return render(request, "management_system/protocols.html", context)

@login_required
def addEmployeeView(request):
    form = EmployeeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("home")
    context={
            "form":form
        }
    return render(request, "management_system/add_new_employee.html", context)
    
@login_required
def itemsView(request):
    itemListQuery = Item.objects.all()
    context={
        "itemList":itemListQuery
    }
    return render(request, "management_system/items.html", context)

@login_required
def singleProtocolView(request,pk):

    context={
        "protocol":Protocol.objects.get(id=pk),
        "items":ProtocolItem.objects.filter(protocol_id=pk)
    }
    return render(request, "management_system/single_protocol.html", context)


@login_required
def singleEmployeeItemsView(request,pk):
    employee = Employee.objects.get(id=pk)
    context={
        "employee":employee,
        "items":Item.objects.filter(item_user=employee)
    }
    return render(request, "management_system/single_employee_items.html", context)

@login_required
def singleEmployeeProtocolsView(request,pk):
    employee = Employee.objects.get(id=pk)
    protocolItems={}

    protocolsList = Protocol.objects.filter(employee=employee)
    for protocol in protocolsList:
        protocolItems[protocol.id]=ProtocolItem.objects.filter(protocol_id=protocol)

    print(protocolItems)
    context={
        "employee":employee,
        "dataSet":protocolItems,
        "protocols":protocolsList
    }
    return render(request, "management_system/single_employee_protocols.html", context)

@login_required
def singleItemView(request,pk):
    item=Item.objects.get(id=pk)
    context={
        "item":item,
        "protocolList":ProtocolItem.objects.filter(item_id=item)

    }
    return render(request, "management_system/single_item.html", context)

@login_required
def employeeItemsReturn(request, employee_id):
    if request.method == "POST":
        listOfItemId = json.loads(request.POST.get("idList"))
        # Process the idList and employee_id as needed
        itemList=[]
        for list_id in listOfItemId:
            itemList.append(Item.objects.get(id=list_id))

        context={
            "dataList":itemList,
            "employee":Employee.objects.get(id=employee_id)
        }
        return render(request, "management_system/return_items.html", context)
    else:
        return HttpResponse("Something went wrong!")


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

class ProtocolList(generics.ListCreateAPIView):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer


class ProtocolDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Protocol.objects.all()
    serializer_class = ProtocolSerializer