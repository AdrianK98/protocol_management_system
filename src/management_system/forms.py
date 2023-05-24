from django import forms
from users.models import Employee
from .models import Protocol, Item,ProtocolItem


class EmployeeForm(forms.ModelForm):
    
    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25'})
        


class ProtocolFormAdd(forms.ModelForm):

    class Meta:
        model = Protocol
        fields = ['employee','item']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})
        self.fields['item'].widget.attrs.update({'id':'search-items'})
        self.fields['employee'].widget.attrs.update({'id':'search-employee'})

    item = forms.ModelChoiceField(
        queryset=Item.objects.filter(item_user__isnull=True),
        required=True,  
    )
    


class ProtocolFormReturn(forms.ModelForm):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(item_user__isnull=False), required=True,)

    class Meta:
        model = Protocol
        fields = ['employee','item']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})
        self.fields['item'].widget.attrs.update({'id':'search-items'})
        self.fields['employee'].widget.attrs.update({'id':'search-employee'})


    # item = forms.ModelChoiceField(
    #     queryset=Item.objects.filter(item_user__isnull=False),
    #     required=True,  
    # )

class ProtocolFormReturnNext(forms.Form):
    item = forms.ModelChoiceField(queryset=Item.objects.filter(item_user__isnull=False), required=True,)
    
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})
        self.fields['item_user'].widget.attrs.update({'id':'search-items','style':'display: none;'})

class ProtocolItemForm(forms.Form):
    item = forms.ModelChoiceField(
        queryset=Item.objects.filter(item_user__isnull=True),
        required=True,  
    )



# 