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
    path("employees/",views.showEmployees, name="employees" ),
    path("new_protocol/",views.newProtocol, name="newprotocol" ),
    path("new_protocol/next/<int:pk>",views.addNextItem, name="addNextItem" ),
    path("protocols/",views.protocolsView, name="protocollist" ),
    path("protocols/<int:pk>",views.singleProtocolView, name="singleProtocol" ),
    path("add_employee/",views.addEmployeeView, name="newemployee" ),
    path("items/",views.itemsView, name="itemsView" ),
    path("api/items",views.ItemList.as_view()),
    path("api/items/<int:pk>",views.ItemDetail.as_view()),
    path("api/employees",views.EmployeeList.as_view()),
    path("api/employees/<int:pk>",views.EmployeeDetail.as_view()),
    path("api/protocols",views.ProtocolList.as_view()),
    path("api/protocols/<int:pk>",views.ProtocolDetail.as_view()),
]

