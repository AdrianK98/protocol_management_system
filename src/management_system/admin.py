from django.contrib import admin
from .models import Item,Protocol,ProtocolItem
# Register your models here.

admin.site.register(Item)
admin.site.register(Protocol)
admin.site.register(ProtocolItem)

