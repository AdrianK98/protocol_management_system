from django import forms
from users.models import Employee
from .models import Protocol, Item,ProtocolItem, Utilization


class EmployeeForm(forms.ModelForm):
    
    class Meta:
        model = Employee
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25'})
        


class ProtocolFormAdd(forms.ModelForm):
    # item = forms.ModelChoiceField(
    #     queryset=Item.objects.filter(item_user__isnull=True,utilization_id__isnull=True),
    #     required=True,  
    # )
    class Meta:
        model = Protocol
        fields = [
            # 'employee','item',
            'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})
        # self.fields['item'].widget.attrs.update({'id':'search-items'})
        self.fields['description'].widget.attrs.update({'id':'protocolDescription'})


    


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
    item = forms.ModelChoiceField(queryset=Item.objects.filter(item_user__isnull=False), required=True)
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})
        self.fields['item'].widget.attrs.update({'id':'search-items'})
    
class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['category', 'item_producent', 'item_model', 'item_sn', 'item_it', 'item_kk',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})

        # 
        #self.fields['item_user'].widget.attrs.update({'id':'search-items','style':'display: none;'})

class UtilizationItemForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=Item.objects.filter(item_user__isnull=True, utilization_id__isnull=True),
        required=True,  
    )
    class Meta:
        model = ProtocolItem
        fields = ['item']

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})
        self.fields['item'].widget.attrs.update({'id':'search-items'})


class UtilizationFinalizationForm(forms.ModelForm):
    class Meta:
        model = Utilization
        fields = ['utilization_company','inform_dzm','company_transfer_date']
        widgets = {
            'company_transfer_date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for field in self.fields: 
            self.fields[field].widget.attrs.update({'class':'w-25 m-2'})
        self.fields['inform_dzm'].widget.attrs.update({'class':'w-5 m-2'})
