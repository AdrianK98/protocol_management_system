from django.db import models
from io import BytesIO
import barcode
from barcode import EAN13
from barcode.writer import ImageWriter

from django.core.files import File
# Create your models here.
class Item(models.Model):
    item_name = models.CharField('Nazwa Przedmiotu',max_length=200)
    item_it = models.CharField('Numer IT',max_length=200,blank=True,null=True)
    item_sn = models.CharField('Numer S/N',max_length=200,blank=True,null=True)
    item_kk = models.CharField("Numer KK",max_length=200,blank=True,null=True)


    def __str__(self):
        return str(self.id) + " "+self.item_name



class Protocol(models.Model):
    created=models.DateField('Data utworzenia',auto_now_add=True)
    barcode=models.CharField(max_length=200,blank=True)
    barcode_img=models.ImageField(upload_to='images/',blank=True)
    barcode_code=models.CharField(max_length=13,blank=True)
    modified=models.DateField('Data modyfikacji',auto_now=True,blank=True,null=True)
    description=models.CharField('Opis',max_length=200,blank=True,null=True)
    is_return=models.BooleanField('Zwrot',blank=True)
    employee=models.ForeignKey("users.Employee", on_delete=models.CASCADE,null=True,verbose_name="Pracownik")

    def save(self, *args, **kwargs):
        EAN = barcode.get_barcode_class('ean13')
        ean = EAN('5901234123457', writer=ImageWriter())
        self.barcode_code = ean
        buffer = BytesIO()
        ean.write(buffer)
        self.barcode_img.save('ssssss.png', File(buffer), save=False)
        super(Protocol, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id)+ " " + str(self.employee) + " " + str(self.created) 


class ProtocolItem(models.Model):
    protocol_id = models.ForeignKey("Protocol", on_delete=models.CASCADE, null=True)
    item_id = models.ForeignKey("Item", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.protocol_id)
    