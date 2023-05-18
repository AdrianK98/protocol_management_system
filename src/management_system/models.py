from django.db import models

# Create your models here.
class Item(models.Model):
    item_name = models.CharField(max_length=200)
    item_it = models.CharField(max_length=200,blank=True,null=True)
    item_sn = models.CharField(max_length=200,blank=True,null=True)
    item_kk = models.CharField(max_length=200,blank=True,null=True)


    def __str__(self):
        return self.item_name


class Protocol(models.Model):
    created=models.DateField(auto_now_add=True)
    barcode=models.CharField(max_length=200)
    modified=models.DateField(auto_now=True,blank=True,null=True)
    description=models.CharField(max_length=200,blank=True,null=True)
    is_return=models.BooleanField(blank=True)
    employee=models.ForeignKey("users.Employee", on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.barcode


class ProtocolItem(models.Model):
    pass