from users.models import Employee
from .models import Item,Protocol, ProtocolItem, Utilization, RegionContent
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse

def get_data_for_region(model, region):
    try:
        if region == None:
            return model.objects.all()
        else:
            content_type = ContentType.objects.get_for_model(model)
            region_ids = RegionContent.objects.filter(content_type=content_type, region=region.id).values_list('object_id', flat=True)
            return model.objects.filter(id__in=region_ids)

    except Exception as e:
        return HttpResponse("ERROR", e)

def get_data_for_region_api(model, region_id):
    try:
        if region_id == None:
            return model.objects.all()
        else:
            content_type = ContentType.objects.get_for_model(model)
            region_ids = RegionContent.objects.filter(content_type=content_type, region=region_id).values_list('object_id', flat=True)
            return model.objects.filter(id__in=region_ids)

    except Exception as e:
        print(e)
        return Exception
    
def save_model_into_region(model,user_region,object_id):
    try:
        content_type = ContentType.objects.get_for_model(model)
        RegionContent.objects.create(
            region = user_region if type(user_region) == int else user_region.id,
            content_type=content_type,
            object_id=object_id
        )
    except Exception as e:
        print(e)
        return Exception
