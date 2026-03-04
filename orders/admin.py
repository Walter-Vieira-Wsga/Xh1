from django.contrib import admin
from .models import Order

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'created_at', 'updated_at', ]  # remove 'slug'

admin.site.register(Order, OrderAdmin)
