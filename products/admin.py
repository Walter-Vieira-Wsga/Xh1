from django.contrib import admin
from .models import Product, ProductImage, Category


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'price', 'active']
    inlines = [ProductImageInline]


admin.site.register(Product, ProductAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug',]


admin.site.register(Category, CategoryAdmin)