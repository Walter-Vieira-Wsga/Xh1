from django import forms
from vendors.models import Vendor

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        #fields = ['company_name', 'cnpj', 'logo', 'description']
        fields = '__all__'