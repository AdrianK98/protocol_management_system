from django import forms
from users.models import Employee
from .models import Protocol, Item


class EmployeeForm(forms.ModelForm):
    
    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25'})
        


class ProtocolForm(forms.ModelForm):
    class Meta:
        model = Protocol
        fields = ['employee','description','is_return']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})

        self.fields['is_return'].widget.attrs.update({'class':'w-1'})

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})