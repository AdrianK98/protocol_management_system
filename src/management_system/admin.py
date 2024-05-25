from django.contrib import admin
from .models import Item,Protocol,ProtocolItem,ItemCategory,Utilization, UserInfo, RegionContent, Region
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
# Register your models here.

class UserInfo(admin.StackedInline):
    model = UserInfo
    can_delete = False
    verbose_name_plural = 'user_region'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserInfo,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Item)
admin.site.register(Protocol)
admin.site.register(ProtocolItem)
admin.site.register(ItemCategory)
admin.site.register(Utilization)
admin.site.register(RegionContent)
admin.site.register(Region)




