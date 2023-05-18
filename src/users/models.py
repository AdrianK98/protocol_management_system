from django.db import models

# Create your models here.

#I SHOULD MOVE IT TO ANOTHER APP
class Employee(models.Model):
    user_name=models.CharField('Imię Pracownika',max_length=200)
    user_surname=models.CharField('Nazwisko Pracownika',max_length=200)
    user_department=models.CharField('Dział',max_length=200,blank=True)
    user_location=models.CharField('Lokalizacja',max_length=200, blank=True)

    def __str__(self):
        return self.user_name +" "+ self.user_surname