from django.urls import path
from vendors import views
from .views import  VendorProductListView


app_name = "vendors"

urlpatterns = [
    path('register/', views.vendor_register, name='vendor_register'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('login/', views.vendor_login, name='vendor_login'),
    path('products/', VendorProductListView.as_view(), name='vendor_products'),

]