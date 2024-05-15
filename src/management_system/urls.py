"""
URL configuration for src project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path("",views.mainView, name="home" ),
    path("employees/",views.EmployeesView.as_view(), name="employees" ),
    path("employees/<int:pk>/items",views.singleEmployeeItemsView, name="singleEmployee" ),
    path("employees/<int:pk>/protocols",views.singleEmployeeProtocolsView, name="singleEmployeeProtocols" ),
    path("new_protocol/add",views.NewProtocolAdd.as_view(), name="newprotocol" ),
    path("new_protocol/return",views.newProtocolReturn, name="newprotocolReturn" ),
    path("new_protocol/confirm/",views.newProtocolReturnConfirm, name="newprotocolconfirm" ),
    # path("new_protocol/next/<str:status>/<int:pk>",views.AddNextItem.as_view(), name="addNextItem" ),
    path("protocols/",views.ProtocolsView.as_view(), name="protocollist" ),
    path("protocols/<int:pk>",views.singleProtocolView, name="singleProtocol" ),
    path("add_employee/",views.addEmployeeView, name="newemployee" ),
    path("add_employee/edit/",views.editEmployeeView.as_view(), name="editEmployee" ),
    path("add_employee/delete/<int:pk>",views.deleteEmployeeView, name="deleteEmployee" ),
    path("items/",views.ItemsView.as_view(), name="itemsView" ),
    path("items/add_new",views.itemsAddNew, name="itemsAddNew" ),
    path("items/edit/<int:pk>",views.itemsEdit, name="itemsEdit" ),
    path("items/<int:pk>",views.singleItemView, name="singleItem" ),
    path("api/items",views.ItemList.as_view()),
    path("api/items/<int:pk>",views.ItemDetail.as_view()),
    path("api/employees",views.EmployeeList.as_view()),
    path("api/employees/<int:pk>",views.EmployeeDetail.as_view()),
    path("api/protocols",views.ProtocolList.as_view()),
    path("api/protocols/<int:pk>",views.ProtocolDetail.as_view()),
    path("employees/<int:employee_id>/returns", views.employeeItemsReturn, name="employeeReturns"),
    path("protocols/view/<int:pk>",views.singleProtocolViewScan, name="singleProtocolScan" ),
    path("utilization/",views.utilizationView.as_view(), name="utilization" ),
    path("utilization/<int:pk>",views.singleUtilizationView.as_view(), name="singleUtilization" ),
    path("utilization/add_item",views.utilizationAddView.as_view(), name="utilizationAddItem" ),
    path("utilization/<int:pk>/finalization",views.utilizationFinalizationView.as_view(), name="utilizationFinalization" ),
    path("utilization/view/<int:pk>",views.singleUtilizationViewScan, name="singleUtilizationScan" ),
    path("utilization/<int:pk>/delete/<int:item>",views.utilizationDeleteItem.as_view(), name="utilizationDeleteItem" ),
    path("utilization/<int:pk>/delete",views.utilizationDelete.as_view(), name="utilizationDelete" ),
    path("api2/employees",views.API2EmployeesView, name="API2Employees" ),
    path("api2/items",views.API2ItemsView, name="API2Items" ),


]

