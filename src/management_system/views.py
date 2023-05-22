from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from rest_framework import generics
import json
from .serializers import ItemSerializer,EmployeeSerializer,ProtocolSerializer
from .forms import EmployeeForm, ProtocolFormAdd, ItemForm, ProtocolFormReturn
from django.contrib import messages


# Create your views here.
from users.models import Employee
from .models import Item,Protocol, ProtocolItem



@login_required
def mainView(request):
    
    return render(request, "management_system/home.html", {})

@login_required
def newProtocolReturnConfirm(request):
    if request.method == 'POST':
        print(request.POST)
        if 'saveAndEnd' in request.POST:

            item_id = request.session.get('item_to_return_id')
            employee_id = request.session.get('employee_item_to_return_id')
            item=Item.objects.get(id=item_id)
            employee=Employee.objects.get(id=employee_id)

            newProtocol = Protocol(employee=employee,is_return=True)
            newProtocol.save()
            newItemProtocol = ProtocolItem(protocol_id=newProtocol,item_id=item).save()
            item.item_user = None
            item.save()
            return redirect("home")
        

        elif 'saveAndContinue' in request.POST:
            return redirect("home")

    context={}
    return render(request, "management_system/confirm_add_protocol.html", context)

@login_required
def showEmployees(request):
    employeeList = Employee.objects.all()
    context={
        "employeeList":employeeList
    }
    return render(request, "management_system/employees.html", context)


@login_required
def itemsAddNew(request):
    itemForm = ItemForm(request.POST or None)
    if request.method == 'POST':
        if itemForm.is_valid():
            try:
                newItem = itemForm.save()
                return redirect('home')
            except:
                print('ERROR OCCURED!')

    context={
        'itemForm':itemForm
    }
    return render(request, "management_system/items_add_new.html", context)





@login_required
def newProtocolReturn(request):
    protocolForm = ProtocolFormReturn(request.POST or None)

    if request.method == 'POST':
        if protocolForm.is_valid():
            try:
                protocolFormData = protocolForm.cleaned_data

                #CHECK IF ITEM THAT WE WANT TO RETURN BELONG TO USER WE WANT TO TAKE IT FROM
                #IF IS RETURN AND USER ITEM IS EMPLOYEE AND ITEM USER IS NOT EMPY
                if protocolFormData['item'].item_user == protocolFormData['employee']:
                    protocolFormData['item'].item_user = None
                    protocolFormData['item'].save()
                    print('OK')

                #IF IS RETURN AND USER ITEM IS NOT EMPLOYEE AND ITEM USER IS NOT EMPTY
                elif protocolFormData['item'].item_user != protocolFormData['employee'] and protocolFormData['item'].item_user :
                    messages.error(request, 'Nie można zwrócic, przedmiot jest używany przez innego użytkownika')
                    return redirect('newProtocol')
                    #CANT COMPLETE
                
                #IF IS RETURN AND USER ITEM IS NOT EMPLOYEE AND ITEM USER IS NOT EMPTY
                elif protocolFormData['item'].item_user != protocolFormData['employee'] and protocolFormData['item'].item_user is None:
                    request.session['item_to_return_id'] = protocolFormData['item'].id
                    request.session['employee_item_to_return_id'] = protocolFormData['employee'].id

                    context={
                        'message':'Przedmiot nie należy do żadnego pracownika',
                    }
                    return render(request,"management_system/confirm_add_protocol.html",context)
                    #TODO add cofirm button


                newProtocol = protocolForm.save(commit=False)
                newProtocol.is_return = True
                newProtocol.save()

                ProtocolItem(protocol_id=newProtocol,item_id=protocolFormData['item']).save()
                if 'saveAndEnd' in request.POST:
                    return redirect("home")
                elif 'saveAndContinue' in request.POST:
                    return redirect("addNextItem",pk=newProtocol.id)
                
            except:
                print("An exception occurred")

    context={
            "protocolForm":protocolForm,
        }
    return render(request, "management_system/new_protocol_return.html", context)


@login_required
def newProtocolAdd(request):
    protocolForm = ProtocolFormAdd(request.POST or None)
    # itemForm = ItemForm(request.POST or None)
    if request.method == 'POST':
            if protocolForm.is_valid():
                try:
                    protocolFormData = protocolForm.cleaned_data
                    #IF ITS NOT RETURN AND USER ITEM IS NOT EMPLOYEE AND ITEM USER IS NOT EMPTY
                    if protocolFormData['item'].item_user != protocolFormData['employee'] and protocolFormData['item'].item_user:
                        return HttpResponse('CANT DO IT')
                        #TODO ADD RETURNING PROTOCOL FROM ACTUAL ITEM USER AND ADD CONFIRM 

                    
                    else:
                        protocolFormData['item'].item_user = protocolFormData['employee']
                        protocolFormData['item'].save()
                    

                    newProtocol = protocolForm.save(commit=False)
                    newProtocol.is_return = False
                    newProtocol.save()
                    ProtocolItem(protocol_id=newProtocol,item_id=protocolFormData['item']).save()
                    if 'saveAndEnd' in request.POST:
                        return redirect("home")
                    elif 'saveAndContinue' in request.POST:
                        return redirect("addNextItem",pk=newProtocol.id)
                    
                except:
                    print("An exception occurred")

    context={
            "protocolForm":protocolForm,
            # "itemForm":itemForm
        }
    return render(request, "management_system/new_protocol_add.html", context)

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
        if 'confirmButton' in request.POST:
            currentEmployee = Employee.objects.get(id=employee_id)
            newProtocol = Protocol(employee=currentEmployee,is_return=True)
            newProtocol.save()
            listOfItemId = request.session['itemsId']
            del request.session['itemsId']
            for itemid in listOfItemId:
                itemObj = Item.objects.get(id=itemid)
                itemObj.item_user = None
                itemObj.save()

                newProtocolItem = ProtocolItem(protocol_id=newProtocol,item_id=itemObj)
                newProtocolItem.save()
            return redirect('singleEmployee',pk=employee_id)
        
        listOfItemId = json.loads(request.POST.get("idList"))
        # Process the idList and employee_id as needed
        itemList=[]
        for list_id in listOfItemId:
            itemList.append(Item.objects.get(id=list_id))
        
        request.session["itemsId"] = listOfItemId

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