from django.urls import path
from orders import views

app_name = 'orders'

urlpatterns = [
    # Carrinho
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # Admin / backoffice
    path('order/<int:order_id>/mark_paid/', views.mark_order_paid, name='mark_order_paid'),
    path('checkout/remove/<int:item_id>/', views.remove_from_order, name='remove_from_order'),
]