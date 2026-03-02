from django import forms
from products.models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        #fields = ['category', 'name', 'description', 'price', 'stock', 'active', ]
        fields = '__all__'

        