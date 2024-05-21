from django.shortcuts import render
from django.views import View
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseNotFound
from management_system.models import Protocol, ProtocolItem, Item
# Create your views here.


class RaportManager(View):
    template = "raports/protocol_template.html"

    def get(self, request):
        protocol = Protocol.objects.get(id=request.GET.get('protocol'))
        protocolItems= ProtocolItem.objects.filter(protocol_id=protocol)
        protocol.printed_count += 1
        protocol.save()



        context={
            'protocol':protocol,
            'protocolItems':protocolItems
        }
        return render(request,self.template,context)
