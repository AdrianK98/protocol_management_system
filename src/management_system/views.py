from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
# Create your views here.


def mainView(request):
    return render(request, "management_system/home.html", {})