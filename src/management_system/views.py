from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import json
from datetime import datetime
from django.utils.decorators import method_decorator
from .forms import EmployeeForm, ProtocolFormAdd, ItemForm, ProtocolFormReturn,ProtocolFormReturnNext,UtilizationItemForm, UtilizationFinalizationForm
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from operator import attrgetter
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .snippets import get_data_for_region
import base64


# TODO: for debug only, delete in release
from pprint import pprint

# Create your views here.
from users.models import Employee
from .models import Item,Protocol, ProtocolItem, Utilization, RegionContent, Region
from django.contrib.contenttypes.models import ContentType
# TODO: Test if item is utilizated while adding new protocol, or in utilization
#TODO ALERT IF ITEM/PROTOCOL/UTILIZATION WITHOUT REGION

    


@method_decorator(login_required, name="dispatch")
class utilizationDelete(View):
    def post(self, request, pk):
        try:
            obj = get_object_or_404(Utilization, id = pk )
            obj.delete()
            return redirect('utilization')
        except Exception as e:
            print('error')
            messages.error(request, f"{e}.")
            return render(request, "management_system/utilization_delete.html", {"utilization": obj})

    def get(self, request, pk):
        try:
            obj = get_object_or_404(Utilization, id = pk)
        except Exception as e:
            print(e)

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
        region=request.user.userinfo.region or None
        queryCreator = str(request.GET.get('qcreator',''))
        queryCreatedDate = str(request.GET.get('qcreateddate',''))
        queryEndDate = str(request.GET.get('qenddate',''))
        utilizationQuery = sorted(self.get_query(queryCreator,queryCreatedDate,queryEndDate,region), key=attrgetter('id'),reverse=True)
        

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
    
    def get_query(self,qcreator,qcreated,qend,region):  # new
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
                     
        object_list = get_data_for_region(Utilization,region).filter(query)

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
            region = request.user.userinfo.region or Region.objects.get(id=request.POST.get('region')) 
            if not region:
                return HttpResponse("ERROR")

            newUtilization = Utilization()
            newUtilization.created_by = request.user
            newUtilization.save()
            try:
                content_type = ContentType.objects.get_for_model(Utilization)
                RegionContent.objects.create(
                    region=region.id,
                    content_type=content_type,
                    object_id=newUtilization.id
                    )
            except Exception as e:
                print(e)
                # Send pk to client in JSON format
            finally:
                return HttpResponse('{\"pk\": \"' + str(newUtilization.id) + '\"}')

        utilizationForm = UtilizationItemForm(request.POST)
        if utilizationForm.is_valid():
            try:
                utilizationFormData = utilizationForm.cleaned_data

                                
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
            return render(request, self.template,{
                'utilizationForm':utilizationFormClass, 
                'pk': pk, 
            })
        else:
            context = {
                'region': request.user.userinfo.region,
                'regions': Region.objects.all()
            }
            return render(request, "management_system/utilization_add_region.html", context)



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
    # print(request.user.userinfo.region)
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
                newItem = itemForm.save(commit=False)
                if request.POST.get('item_user'):
                    newItem.item_user = Employee.objects.get(id=request.POST.get('item_user'))

                newItem.save()

                region = request.user.userinfo.region or Region.objects.get(id=request.POST.get('region'))
                content_type = ContentType.objects.get_for_model(Item)
                RegionContent.objects.create(
                    region=region.id,
                    content_type=content_type,
                    object_id=newItem.id
                    )
                
                
            except Exception as e:
                print(e)
            finally:
                return redirect('home')
        else:
            print('Form not valid!')
            print(itemForm.errors)

    context={
        'itemForm':itemForm,
        'region': request.user.userinfo.region,
        'regions': Region.objects.all() 
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
                    # print('OK')

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

                region = request.user.userinfo.region or Region.objects.get(id=request.POST.get('region'))
                content_type = ContentType.objects.get_for_model(Protocol)
                try:
                    RegionContent.objects.create(
                    region=region.id,
                    content_type=content_type,
                    object_id=newProtocol.id
                    )
                except Exception as e:
                    print('Failed protocol to save into region content!')
                    print(e)


                ProtocolItem(protocol_id=newProtocol,item_id=protocolFormData['item']).save()
                if 'saveAndEnd' in request.POST:
                    return redirect("singleProtocol",pk=newProtocol.id)
                elif 'saveAndContinue' in request.POST:
                    return redirect("addNextItem",status='return',pk=newProtocol.id)
                
            except:
                print("An exception occurred")

    context={
            "protocolForm":protocolForm,
            'region': request.user.userinfo.region,
            'regions': Region.objects.all()
        }
    return render(request, "management_system/new_protocol_return.html", context)


@method_decorator(login_required, name="dispatch")
class EmployeesView(View):
    def get(self,request):
        region = request.user.userinfo.region or None
        queryName = str(request.GET.get('qname',''))
        querySurname = str(request.GET.get('qsurname',''))

        employeeQuery = sorted(self.get_query(queryName,querySurname,region), key=attrgetter('id'),reverse=True)
        

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


    def get_query(self,qname,qsurname,region):  # new
        query = Q()
        if qname:
            query = query & (
                Q(user_name__icontains=qname)
            )

        if qsurname:
            query = query & (
                Q(user_surname__icontains=qsurname)
            )   
        
        object_list = get_data_for_region(Employee,region).filter(query)
        # object_list = Employee.objects.filter(query)

        return object_list
    
@method_decorator(login_required, name="dispatch")
class ProtocolsView(View):

    def get(self,request):
        region = request.user.userinfo.region or None
        queryName = str(request.GET.get('qname',''))
        querySurname = str(request.GET.get('qsurname',''))
        queryDate = str(request.GET.get('qdate',''))
        queryBarcode = str(request.GET.get('qbarcode',''))
        protocolQuery = sorted(self.get_query(queryName,querySurname,queryDate,queryBarcode,region), key=attrgetter('id'),reverse=True)
        

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
    
    def get_query(self,qname,qsurname,qdate,qbarcode,region):  # new
        query = Q()
        if qname:
            query = query & (
                Q(employee__user_name__icontains=qname)
            )

        if qsurname:
            query = query & (
                Q(employee__user_surname__icontains=qsurname)
            )   
        
        if qbarcode:
            query = query & (
                Q(barcode__icontains=qbarcode)
            )   

        if qdate:
            date = datetime.strptime(qdate, '%Y-%m-%d').date()
            query = query & (
                Q(created__icontains=date)
            )                       
        object_list = get_data_for_region(Protocol,region).filter(query)
        return object_list

@login_required
def addEmployeeView(request):
    form = EmployeeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                newEmployee = form.save()
                region = request.user.userinfo.region or Region.objects.get(id=request.POST.get('region'))

                content_type = ContentType.objects.get_for_model(Employee)
                try:
                    RegionContent.objects.create(
                    region=region.id,
                    content_type=content_type,
                    object_id=newEmployee.id
                    )
                except Exception as e:
                    print('Failed employee to save into region content!')
                    print(e)
            except Exception as e:
                print(e)
            return redirect("employees")
    context={
            "form":form,
            'region': request.user.userinfo.region,
            'regions': Region.objects.all()
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
        region = request.user.userinfo.region or None
        queryType = str(request.GET.get('qtype',''))
        queryModel = str(request.GET.get('qmodel',''))
        queryIt = str(request.GET.get('qit',''))
        querySn = str(request.GET.get('qsn',''))
        queryKk = str(request.GET.get('qkk',''))
        queryQused = request.GET.get('qused','')
        itemQuery = sorted(self.get_query(queryType,queryModel,queryIt,querySn,queryKk,queryQused,region), key=attrgetter('id'),reverse=True)
        
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
    
    def get_query(self,qtype,qmodel,qit,qsn,qkk,qused,region):  # new
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
        object_list = get_data_for_region(Item,region).filter(query)
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
                protocolFormData = protocolForm.save(commit=False)
                protocolFormData.item = Item.objects.get(id=request.POST['item'])
                protocolFormData.employee = Employee.objects.get(id=request.POST['employee'])
                
                #IF ITS NOT RETURN AND USER ITEM IS NOT EMPLOYEE AND ITEM USER IS NOT EMPTY
                if protocolFormData.item.item_user != protocolFormData.employee and protocolFormData.item.item_user:
                    return HttpResponse('CANT DO IT')
                    #TODO ADD RETURNING PROTOCOL FROM ACTUAL ITEM USER AND ADD CONFIRM 
                else:
                    protocolFormData.item.item_user = protocolFormData.employee
                    protocolFormData.item.save()
                    
                # If pk was send to us, we use it otherwise we create new protocol
                if 'pk' in request.POST:
                    newProtocol = Protocol.objects.get(id=request.POST['pk'])
                    region = request.user.userinfo.region or Region.objects.get(id=request.POST.get('region'))
                    content_type = ContentType.objects.get_for_model(Protocol)
                    RegionContent.objects.create(
                        region=region.id,
                        content_type=content_type,
                        object_id=newProtocol.id
                    )
                else:
                    newProtocol = protocolFormData
                    newProtocol.is_return = False
                    newProtocol.created_by = request.user
                    newProtocol.save()

                ProtocolItem(protocol_id=newProtocol,item_id=protocolFormData.item).save()

                
                return HttpResponse('{\"pk\": \"' + str(newProtocol.id) + '\"}')
                
            except Exception as e:
                print(e)
                return HttpResponse('ERROR')
            finally:
                return HttpResponse('{\"pk\": \"' + str(newProtocol.id) + '\"}')
        else:
            print("Form is invalid")
        return HttpResponse('ERROR')

    def get(self,request):
        if request.GET.get('eid'):
            # protocolFormClass = ProtocolFormAdd
            # protocolForm = protocolFormClass(initial={
            #     'employee': Employee.objects.get(id=request.GET.get('eid'))
            # })
            return render(request, self.template,{'employee':Employee.objects.get(id=request.GET.get('eid'))})
        else:
            protocolFormClass = ProtocolFormAdd
            return render(request, self.template,{'protocolForm':protocolFormClass,
            'region': request.user.userinfo.region,
            'regions': Region.objects.all()})


