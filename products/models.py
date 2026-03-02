from django.db import models
from vendors.models import Vendor

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, verbose_name='Vendedor: ')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Categoria: ')

    name = models.CharField(max_length=255, verbose_name='Produto; ')
    slug = models.SlugField(unique=True, verbose_name='Slug: ')  # 👈 ADICIONAR
    description = models.TextField(blank=True, verbose_name='Descrição: ')
    name_brand = models.CharField(max_length=30, verbose_name='Nome da Marca: ')
    manufacturer = models.CharField(max_length=30, verbose_name='Fabricante: ')
    model_product = models.CharField(max_length=30, verbose_name='Modelo: ')
    name_model_product = models.CharField(max_length=20, verbose_name='Nome do Modelo: ')
    color_product = models.CharField(max_length=30, verbose_name='Cor: ')
    inmetro_register = models.CharField(max_length=30, verbose_name='Registro no INMETRO: ')
    part_number = models.CharField(max_length=20, verbose_name='Número da Peça: ')
    special_features_product = models.CharField(max_length=50, verbose_name='Caracteristicas Especiais: ')
    unit_number_product = models.CharField(max_length=20, verbose_name='Número de Unidades: ')
    power_voltage_product = models.CharField(max_length=15, verbose_name='Voltagem: ')
    power_watts_product = models.CharField(max_length=15, verbose_name='Potência em Watts: ')
    type_energy_source_product = models.CharField(max_length=30, verbose_name='Tipo de Fonte: ')
    batteries_included = models.BooleanField(default=True, verbose_name='Baterias Inclusas: ')
    cells_batteries = models.CharField(max_length=15, verbose_name='Celulas de Baterias: ')
    works_batteries = models.BooleanField(default=True, verbose_name='Funciona com baterias: ')
    diameter_product = models.CharField(max_length=25, verbose_name='Diametro do Produto: ')
    package_dimensions = models.CharField(max_length=30, verbose_name='Dimensões do Pacote: ')
    type_material_product = models.CharField(max_length=30,verbose_name='Tipo de Material: ')
    contains_liquid = models.BooleanField(default=True, verbose_name='Contêm Líquido: ')
    asin_product = models.CharField(max_length=30, verbose_name='Código ASIN: ')
    ean_product = models.CharField(max_length=30, verbose_name='Código EAN: ')
    ncm = models.CharField(max_length=30, verbose_name='Código NCM: ')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço do Produto: ')
    stock = models.PositiveIntegerField(default=0, verbose_name='Estoque: ')
    active = models.BooleanField(default=True, verbose_name='Produto Ativo: ')


    def __str__(self):
        return self.name

    def main_image(self):
        return self.images.filter(is_main=True).first() or self.images.first()    
    
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/images/")
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Imagem de {self.product.name}"    
    
