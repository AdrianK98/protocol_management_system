from users.models import Employee
from .models import Item,Protocol, ProtocolItem, Utilization, RegionContent
from django.contrib.contenttypes.models import ContentType

def get_data_for_region(model, region):
    try:
        if region == None:
            return model.objects.all()
        else:
            content_type = ContentType.objects.get_for_model(model)
            region_ids = RegionContent.objects.filter(content_type=content_type, region=region.id).values_list('object_id', flat=True)
            return model.objects.filter(id__in=region_ids)
        return Exception
    except Exception as e:
        print(e)
