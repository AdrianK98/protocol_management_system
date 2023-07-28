from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from rest_framework import generics
import json
from datetime import datetime
from django.utils.decorators import method_decorator
from .serializers import ItemSerializer,EmployeeSerializer,ProtocolSerializer
from .forms import EmployeeForm, ProtocolFormAdd, ItemForm, ProtocolFormReturn, ProtocolItemForm,ProtocolFormReturnNext
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from operator import attrgetter


# Create your views here.
from users.models import Employee
from .models import Item,Protocol, ProtocolItem




@login_required
def deleteEmployeeView(request,pk):
    
    # fetch the object related to passed id
    obj = get_object_or_404(Employee, id = pk)
    context ={
        'employee':obj,
    }
    if request.method =="POST":
        try:
            obj.delete()
            return redirect("employees")
        except Exception as e:
            messages.error(request, f"{e}.")
            return redirect("deleteEmployee",pk=pk)

    return render(request, "management_system/delete_employee.html", context)

@login_required
def itemsEdit(request,pk):

    context ={}
 
    # fetch the object related to passed id
    obj = get_object_or_404(Item, id = pk)
 
    # pass the object as instance in form
    form = ItemForm(request.POST or None, instance = obj)
 
    # save the data from the form and
    # redirect to detail_view
    if form.is_valid():
        try:
            form.save()
            return redirect("itemsView")
        except Exception as e:
            return HttpResponse(f"{e}")
    context["itemForm"] = form
    return render(request, "management_system/items_edit.html", context)

@method_decorator(login_required, name="dispatch")
class editEmployeeView(View):
    def post(self, request):
        obj = get_object_or_404(Employee, id = request.GET.get('id',''))
        form = EmployeeForm(request.POST or None,instance = obj)
        if form.is_valid():
            form.save()
            return redirect("employees")
        context={
            "form":form
        }
        return render(request, "management_system/edit_employee.html", context)

    def get(self, request):
        obj = get_object_or_404(Employee, id = request.GET.get('id',''))
        form = EmployeeForm(instance = obj)
        context={
                "form":form
            }
        return render(request, "management_system/edit_employee.html", context)

@login_required
def mainView(request):
    print(request.user.first_name)
    print(request.user.last_name)
    return render(request, "management_system/home.html", {})

@login_required
def newProtocolReturnConfirm(request):
    if request.method == 'POST':
        print(request.POST)
        if 'saveAndEnd' in request.POST:

            item_id = request.session.get('item_to_return_id')
            employee_id = request.session.get('employee_item_to_return_id')
            del request.session['item_to_return_id']
            del request.session['employee_item_to_return_id']
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
                newProtocol.created_by = request.user
                newProtocol.save()

                ProtocolItem(protocol_id=newProtocol,item_id=protocolFormData['item']).save()
                if 'saveAndEnd' in request.POST:
                    return redirect("singleProtocol",pk=newProtocol.id)
                elif 'saveAndContinue' in request.POST:
                    return redirect("addNextItem",status='return',pk=newProtocol.id)
                
            except:
                print("An exception occurred")

    context={
            "protocolForm":protocolForm,
        }
    return render(request, "management_system/new_protocol_return.html", context)


@method_decorator(login_required, name="dispatch")
class AddNextItem(View):

    def post(self,request,status,pk):
        if status == 'add':
            self.addItem(request,status,pk)
            if 'saveAndEnd' in request.POST:
                return redirect("singleProtocol",pk=pk)
            elif 'saveAndContinue' in request.POST:
                return redirect("addNextItem",status='add',pk=pk)
        elif status == 'return':
            return self.returnItem(request,status,pk)

    
    def get(self,request,status,pk):
        if status == 'add':
            return render(request, "management_system/new_protocol_next_item.html", {'itemForm':ProtocolItemForm,"pk":pk})
        return render(request, "management_system/new_protocol_next_item.html", {'itemForm':ProtocolFormReturnNext,"pk":pk})

    def addItem(self,request,status,pk):
        itemForm = ProtocolItemForm(request.POST)
        if itemForm.is_valid(): 
            newProtocol = Protocol.objects.get(id=pk)
            try:
                itemFormData= itemForm.cleaned_data
                newItem = itemFormData['item']
                itemFormData['item'].item_user = newProtocol.employee
                itemFormData['item'].save()
                ProtocolItem(protocol_id=newProtocol,item_id=newItem).save()
                print('valid')
            except:
                return HttpResponse('ERROR')
    
    def returnItem(self,request,status,pk):
        itemForm = ProtocolFormReturnNext(request.POST)
        if itemForm.is_valid(): 
            newProtocol = Protocol.objects.get(id=pk)
            employee = newProtocol.employee
            try:
                itemFormData= itemForm.cleaned_data
                newItem = itemFormData['item']

                if newItem.item_user != employee and newItem.item_user :
                    messages.error(request, 'Nie można zwrócic, przedmiot jest używany przez innego użytkownika')
                    print('NOT THIS USER')
                    return redirect("addNextItem",status='return',pk=pk)


                itemFormData['item'].item_user = None
                itemFormData['item'].save()
                ProtocolItem(protocol_id=newProtocol,item_id=newItem).save()
                if 'saveAndEnd' in request.POST:
                    return redirect("singleProtocol",pk=pk)
                elif 'saveAndContinue' in request.POST:
                    return redirect("addNextItem",status='return',pk=pk)
            except:
                return HttpResponse('ERROR')


@method_decorator(login_required, name="dispatch")
class EmployeesView(View):
    def get(self,request):
        queryName = str(request.GET.get('qname',''))
        querySurname = str(request.GET.get('qsurname',''))
        employeeQuery = sorted(self.get_query(queryName,querySurname), key=attrgetter('id'),reverse=True)
        

        page = request.GET.get('page',1)
        protocols_paginator = Paginator(employeeQuery,20)

        try:
            employeeQuery = protocols_paginator.page(page)
        except PageNotAnInteger:
            employeeQuery = protocols_paginator.page(1)
        except EmptyPage:
            employeeQuery = protocols_paginator.page(1)

        context={
            "employeeList":employeeQuery,
            "qname_value": queryName,
            "qsurname_value": querySurname,
        }
        return render(request, "management_system/employees.html", context)


    def get_query(self,qname,qsurname):  # new
        query = Q()
        if qname:
            query = query & (
                Q(user_name__icontains=qname)
            )

        if qsurname:
            query = query & (
                Q(user_surname__icontains=qsurname)
            )   
                     
        object_list = Employee.objects.filter(query)

        return object_list
    
@method_decorator(login_required, name="dispatch")
class ProtocolsView(View):

    def get(self,request):
        queryName = str(request.GET.get('qname',''))
        querySurname = str(request.GET.get('qsurname',''))
        queryDate = str(request.GET.get('qdate',''))
        protocolQuery = sorted(self.get_query(queryName,querySurname,queryDate), key=attrgetter('id'),reverse=True)
        

        page = request.GET.get('page',1)
        protocols_paginator = Paginator(protocolQuery,20)

        try:
            protocolQuery = protocols_paginator.page(page)
        except PageNotAnInteger:
            protocolQuery = protocols_paginator.page(1)
        except EmptyPage:
            protocolQuery = protocols_paginator.page(1)

        context={
            "protocolList":protocolQuery,
            "qname_value": queryName,
            "qsurname_value": querySurname,
            "qdate_value": queryDate
        }
        return render(request, "management_system/protocols.html", context)
    
    def get_query(self,qname,qsurname,qdate):  # new
        query = Q()
        if qname:
            query = query & (
                Q(employee__user_name__icontains=qname)
            )

        if qsurname:
            query = query & (
                Q(employee__user_surname__icontains=qsurname)
            )   

        if qdate:
            date = datetime.strptime(qdate, '%d.%m.%Y').date()
            query = query & (
                Q(created__icontains=date)
            )                       
        object_list = Protocol.objects.filter(query)
        return object_list

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

@method_decorator(login_required, name="dispatch")
class ItemsView(View):
    def get(self,request):
        queryType = str(request.GET.get('qtype',''))
        queryModel = str(request.GET.get('qmodel',''))
        queryIt = str(request.GET.get('qit',''))
        querySn = str(request.GET.get('qsn',''))
        queryKk = str(request.GET.get('qkk',''))
        queryQused = request.GET.get('qused','')
        itemQuery = sorted(self.get_query(queryType,queryModel,queryIt,querySn,queryKk,queryQused), key=attrgetter('id'),reverse=True)
        
        page = request.GET.get('page',1)
        protocols_paginator = Paginator(itemQuery,20)

        try:
            itemQuery = protocols_paginator.page(page)
        except PageNotAnInteger:
            itemQuery = protocols_paginator.page(1)
        except EmptyPage:
            itemQuery = protocols_paginator.page(1)

        context={
            "itemList":itemQuery,
            "qtype_value": queryType,
            "qmodel_value": queryModel,
            "qit_value": queryIt,
            "qsn_value": querySn,
            "qkk_value": queryKk,
            "qused": queryQused,

        }
        return render(request, "management_system/items.html", context)
    
    def get_query(self,qtype,qmodel,qit,qsn,qkk,qused):  # new
        query = Q()
        if qtype:
            query = query & (
                Q(category__category_name__icontains=qtype)
            )
        if qmodel:
            query = query & (
                Q(item_model__icontains=qmodel)
            )   

        if qit:
            query = query & (
                Q(item_it__icontains=qit)
            )
        if qsn:
            query = query & (
                Q(item_sn__icontains=qsn)
            )

        if qkk:
            query = query & (
                Q(item_kk__icontains=qkk)
            )
        if qused:
            query = query & (
                Q(item_user__isnull=False)
            )    
        object_list = Item.objects.filter(query)
        return object_list  

@login_required
def singleProtocolView(request,pk):

    context={
        "protocol":Protocol.objects.get(id=pk),
        "items":ProtocolItem.objects.filter(protocol_id=pk),
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
            newProtocol = Protocol(employee=currentEmployee,is_return=True,created_by=request.user)
            newProtocol.save()
            listOfItemId = request.session['itemsId']
            del request.session['itemsId']
            for itemid in listOfItemId:
                itemObj = Item.objects.get(id=itemid)
                itemObj.item_user = None
                itemObj.save()

                newProtocolItem = ProtocolItem(protocol_id=newProtocol,item_id=itemObj)
                newProtocolItem.save()
            return redirect("singleProtocol",pk=newProtocol.id)
        
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



@method_decorator(login_required, name="dispatch")
class NewProtocolAdd(View):
    template = "management_system/new_protocol_add.html"
    def post(self,request):
        protocolForm = ProtocolFormAdd(request.POST)
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
                newProtocol.created_by = request.user
                
                newProtocol.save()
                ProtocolItem(protocol_id=newProtocol,item_id=protocolFormData['item']).save()
                if 'saveAndEnd' in request.POST:
                    return redirect("singleProtocol",pk=newProtocol.id)
                elif 'saveAndContinue' in request.POST:
                    return redirect("addNextItem",status='add',pk=newProtocol.id)
                
            except:
                    return HttpResponse('ERROR')

    def get(self,request):
        if request.GET.get('eid'):
            protocolFormClass = ProtocolFormAdd
            protocolForm = protocolFormClass(initial={
                'employee': Employee.objects.get(id=request.GET.get('eid'))
            })
            return render(request, self.template,{'protocolForm':protocolForm})
        else:
            protocolFormClass = ProtocolFormAdd
            return render(request, self.template,{'protocolForm':protocolFormClass})





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