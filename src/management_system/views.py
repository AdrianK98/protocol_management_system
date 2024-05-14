from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from rest_framework import generics
import json
from datetime import datetime
from django.utils.decorators import method_decorator
from .serializers import ItemSerializer,EmployeeSerializer,ProtocolSerializer
from .forms import EmployeeForm, ProtocolFormAdd, ItemForm, ProtocolFormReturn,ProtocolFormReturnNext,UtilizationItemForm, UtilizationFinalizationForm
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from operator import attrgetter
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import base64


# TODO: for debug only, delete in release
from pprint import pprint

# Create your views here.
from users.models import Employee
from .models import Item,Protocol, ProtocolItem, Utilization

# TODO: Test if item is utilizated while adding new protocol, or in utilization

@method_decorator(login_required, name="dispatch")
class utilizationDelete(View):
    def post(self, request, pk):
        obj = get_object_or_404(Utilization, id = pk )
        obj.delete()
        return redirect('utilization')

    def get(self, request, pk):
        obj = get_object_or_404(Utilization, id = pk)
        context={
            "utilization": obj,
            "pk":pk,
        }
        return render(request, "management_system/utilization_delete.html", context)


@method_decorator(login_required, name="dispatch")
class utilizationDeleteItem(View):
    def post(self, request, pk, item):
        obj = get_object_or_404(Utilization, id = pk )
        it = get_object_or_404(Item, id = item)
        it.utilization_id = None
        it.save()
        return redirect('singleUtilization', pk)

    def get(self, request, pk, item):
        obj = get_object_or_404(Utilization, id = pk)
        it = get_object_or_404(Item, id = item)
        context={
            "utilization": obj,
            "item": it,
            "pk":pk,
            "item_id":item
        }
        return render(request, "management_system/utilization_delete_item.html", context)


@login_required
def singleUtilizationViewScan(request,pk):
    obj = Utilization.objects.get(id=pk)
    blob = base64.b64decode(obj.utilization_protocol_scan)
    return HttpResponse(blob, content_type='application/pdf')

@method_decorator(login_required, name="dispatch")
class utilizationFinalizationView(View):
    def post(self, request, pk):
        obj = get_object_or_404(Utilization, id = pk )
        form = UtilizationFinalizationForm(request.POST, instance = obj)
        if request.FILES:
            scan_binary_blob = base64.b64encode(request.FILES.get('scan').read())
        if form.is_valid():
            try:
                form.save()
                obj.utilization_protocol_scan = scan_binary_blob
                obj.save()
                return redirect('home')
            except Exception as e:
                print(e)
                return redirect('home')
        print('WRONG FORM!')    
        return redirect('home')

    def get(self, request, pk):
        # form = EmployeeForm(instance = obj)
        obj = get_object_or_404(Utilization, id = pk)
        utilizationForm = UtilizationFinalizationForm(instance = obj)
        context={
        "utilizationForm":utilizationForm,
            "utilization": obj,
        "pk":pk,
        }
        return render(request, "management_system/utilization_finalization.html", context)
    


@method_decorator(login_required, name="dispatch")
class utilizationView(View):
    def get(self, request):

        queryCreator = str(request.GET.get('qcreator',''))
        queryCreatedDate = str(request.GET.get('qcreateddate',''))
        queryEndDate = str(request.GET.get('qenddate',''))
        utilizationQuery = sorted(self.get_query(queryCreator,queryCreatedDate,queryEndDate), key=attrgetter('id'),reverse=True)
        

        page = request.GET.get('page',1)
        protocols_paginator = Paginator(utilizationQuery,20)

        try:
            utilizationQuery = protocols_paginator.page(page)
        except PageNotAnInteger:
            utilizationQuery = protocols_paginator.page(1)
        except EmptyPage:
            utilizationQuery = protocols_paginator.page(1)

        context={
        "utilizationList":utilizationQuery,
        "qcreator_value": queryCreator,
        "qcreateddate_value": queryCreatedDate,
        "qenddate_value": queryEndDate,
        
        }
        return render(request, "management_system/utilization.html", context)
    
    def get_query(self,qcreator,qcreated,qend):  # new
        query = Q()
        if qcreator:
            query = query & (
                Q(created_by__username__icontains=qcreator)
            )

        if qcreated:
            date1 = datetime.strptime(qcreated, '%Y-%m-%d').date()
            query = query & (
                Q(created__icontains=date1)
            )

        if qend:
            date2 = datetime.strptime(qend, '%Y-%m-%d').date()
            query = query & (
                Q(company_transfer_date__icontains=date2)
            )      
                     
        object_list = Utilization.objects.filter(query)

        return object_list
    
@method_decorator(login_required, name="dispatch")
class singleUtilizationView(View):
    def get(self, request, pk):
        utilizationObj = get_object_or_404(Utilization, id = pk)

        context={
        "utilization":utilizationObj,
        "items":Item.objects.filter(utilization_id=utilizationObj)
        }
        return render(request, "management_system/single_utilization.html", context)


@method_decorator(login_required, name="dispatch")
class utilizationAddView(View):
    template = "management_system/utilization_add_item.html"

    def post(self,request):
        # If pk was send to us, we use it otherwise we create new protocol
        if 'pk' in request.POST:
            newUtilization = Utilization.objects.get(id=request.POST['pk'])
        else:
            newUtilization = Utilization()
            newUtilization.created_by = request.user
            newUtilization.save()
            # Send pk to client in JSON format
            return HttpResponse('{\"pk\": \"' + str(newUtilization.id) + '\"}')

        utilizationForm = UtilizationItemForm(request.POST)
        if utilizationForm.is_valid():
            try:
                utilizationFormData = utilizationForm.cleaned_data

                pprint(request.POST)

                                
                #IF ITS NOT RETURN AND USER ITEM IS NOT EMPLOYEE AND ITEM USER IS NOT EMPTY
                if utilizationFormData['item'].item_user:
                    return HttpResponse('CANT DO IT')
                    #TODO ADD RETURNING PROTOCOL FROM ACTUAL ITEM USER AND ADD CONFIRM 
                else:
                    utilizationFormData['item'].utilization_id = newUtilization
                    utilizationFormData['item'].save()
                    
                
                # Send pk to client in JSON format
                return HttpResponse('{\"pk\": \"' + str(newUtilization.id) + '\"}')
                
            except Exception as e:
                print(e)
                return HttpResponse('ERROR')
        else:
            print("Form is invalid")
        return HttpResponse('ERROR')


    def get(self, request):
        pk = 'undefined'
        if 'pk' in request.GET:
            pk = request.GET['pk']
        utilizationFormClass = UtilizationItemForm
        return render(request, self.template,{'utilizationForm':utilizationFormClass, 'pk': pk})



@login_required
def singleProtocolViewScan(request,pk):
    obj = Protocol.objects.get(id=pk)
    blob = base64.b64decode(obj.protocol_scan)
    return HttpResponse(blob, content_type='application/pdf')

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


#TODO CLEAN UP
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
            date = datetime.strptime(qdate, '%Y-%m-%d').date()
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
                    
                
                pprint(request.POST)

                # If pk was send to us, we use it otherwise we create new protocol
                if 'pk' in request.POST:
                    newProtocol = Protocol.objects.get(id=request.POST['pk'])
                else:
                    newProtocol = protocolForm.save(commit=False)
                    newProtocol.is_return = False
                    newProtocol.created_by = request.user
                    newProtocol.save()

                ProtocolItem(protocol_id=newProtocol,item_id=protocolFormData['item']).save()

                # This if is not used by me, but i decided not to delete it just in case
                if 'saveAndEnd' in request.POST:
                    return redirect("singleProtocol",pk=newProtocol.id)
                elif 'saveAndContinue' in request.POST:
                    return redirect("addNextItem",status='add',pk=newProtocol.id)
                
                # Send pk to client in JSON format
                return HttpResponse('{\"pk\": \"' + str(newProtocol.id) + '\"}')
                
            except Exception as e:
                print(e)
                return HttpResponse('ERROR')
        else:
            print("Form is invalid")
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
