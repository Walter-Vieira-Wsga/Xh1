from django.urls import path
from vendors import views
from .views import  VendorProductListView


app_name = "vendors"

urlpatterns = [
    path('register/', views.vendor_register, name='vendor_register'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('login/', views.vendor_login, name='vendor_login'),
    path('products/', VendorProductListView.as_view(), name='vendor_products'),
    path("orders1/", views.vendor_orders, name="vendor_orders"),
    path("orders/", views.vendor_orders_dashboard, name="vendor_orders_dashboard"),
    path("orders/ship/<int:item_id>/", views.mark_item_shipped, name="mark_item_shipped"),
    path("orders/advance/<int:item_id>/", views.advance_order_status, name="advance_order_status"),
    path("orders/cancel/<int:item_id>/", views.cancel_order_item, name="cancel_order_item"),

]