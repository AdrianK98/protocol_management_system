from django.db import models
from io import BytesIO
from django.conf import settings
import barcode
from barcode.writer import ImageWriter
from datetime import datetime

from django.core.files import File
# Create your models here.


DATE_INPUT_FORMATS = ['%d-%m-%Y']

class Item(models.Model):
    category = models.ForeignKey("ItemCategory", on_delete=models.PROTECT,null=True,blank=False,verbose_name="Kategoria")
    item_producent = models.CharField('Producent',max_length=200)
    item_model = models.CharField('Model',max_length=200)
    item_sn = models.CharField('Numer S/N',max_length=200)
    item_it = models.CharField('Numer IT',max_length=200,blank=True,null=True)
    item_kk = models.CharField("Numer KK",max_length=200,blank=True,null=True)
    item_user = models.ForeignKey("users.Employee", on_delete=models.PROTECT,null=True,blank=True,verbose_name="Pracownik")
    utilization_id = models.ForeignKey("management_system.Utilization", on_delete=models.PROTECT,null=True,blank=True,verbose_name="Utylizacja")



    def __str__(self):
        mid = " " + self.item_producent + " " + self.item_model
        if self.item_it:
            mid = self.item_it + mid
        else:
            mid = "NOIT" + mid
        return mid



class Protocol(models.Model):
    created=models.DateField('Data utworzenia',auto_now_add=True)
    barcode=models.CharField(max_length=20,blank=True, unique=True)
    modified=models.DateField('Data modyfikacji',auto_now=True,blank=True,null=True)
    description=models.CharField('Opis',max_length=200,blank=True,null=True)
    is_return=models.BooleanField('Zwrot',blank=True)
    printed_count=models.IntegerField('Druk',default=0,blank=True)
    is_scanned=models.BooleanField('Skan',default=False, null=False, blank=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,blank=True,null=True
    )
    employee=models.ForeignKey("users.Employee", on_delete=models.CASCADE,null=True,verbose_name="Pracownik")
    protocol_scan = models.BinaryField('SkanProtokolu',blank=True,null=True, editable=True)


    def save(self, *args, **kwargs):
        currentDay = str(datetime.now().day)
        currentMonth = str(datetime.now().month)
        currentYear = str(datetime.now().year)
        currentSecond= str(datetime.now().second)
        currentMinute = str(datetime.now().minute)
        currentHour = str(datetime.now().hour) 
        employeeId= str(self.employee.id)
        ean = f'{currentYear.zfill(4)}{currentMonth.zfill(2)}{currentDay.zfill(2)}{currentMinute.zfill(2)}{currentSecond.zfill(2)}{employeeId.zfill(2)}'
        self.barcode = ean
        # buffer = BytesIO()
        # ean.write(buffer)
        # self.barcode_img.save(f'{ean}.png', File(buffer), save=False)
        super(Protocol, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)+ " " + str(self.employee) + " " + str(self.created) 


class ProtocolItem(models.Model):
    protocol_id = models.ForeignKey("Protocol", on_delete=models.CASCADE, null=True)
    item_id = models.ForeignKey("Item", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.protocol_id) + " | " + str(self.item_id)
    

class ItemCategory(models.Model):
    category_name = models.CharField("Typ", null=False,max_length=200)

    def __str__(self):
        return self.category_name
    

class Utilization(models.Model):
    created=models.DateField('Data utworzenia',auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,blank=True,null=True
    )
    utilization_company = models.CharField('Firma utylizujaca',blank=True,max_length=200)
    inform_dzm = models.BooleanField('Ponfirmowano DZM',blank=False, default=False)
    utilization_protocol_scan = models.BinaryField('Skan protokolu utylizacji',blank=True,null=True, editable=True, default=None)
    company_transfer_date=models.DateField('Data przekazania firmie zewnetrznej',auto_now=True,blank=True,null=True)

    def __str__(self):
        return 'id ' + str(self.id) + '  date '+str(self.created)