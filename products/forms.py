from django import forms
from products.models import Product, ProductImage
from django.forms import inlineformset_factory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'slug', 'description', 'name_brand', 'manufacturer', 
        'model_product','name_model_product','color_product','inmetro_register',
        'part_number', 'special_features_product', 'unit_number_product', 'power_voltage_product', 
        'power_watts_product','type_energy_source_product', 'batteries_included', 'cells_batteries',
        'works_batteries', 'diameter_product', 'package_dimensions', 'type_material_product', 
        'contains_liquid', 'asin_product', 'ean_product', 'ncm', 'price', 'stock', 'active', ]
        exclude = ['slug', 'vendor']  # 🔒 não expõe slug
        
      

ProductImageFormSet = inlineformset_factory(
    Product,
    ProductImage,
    fields=('image', 'is_main'),
    extra=1,
    can_delete=True
)