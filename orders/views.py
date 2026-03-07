from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib import messages

from orders.models import (
    CartItem,
    Order,
    OrderItem,
    VendorPayout, 
    Cart
)

from products.models import Product


# ======================================================
# CARRINHO
# ======================================================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('orders:view_cart')


@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in cart_items)

    return render(request, 'orders/cart.html', {
        'cart_items': cart_items,
        'total': total
    })


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, user=request.user)
    item.delete()
    return redirect('orders:view_cart')


# ======================================================
# CHECKOUT
# ======================================================

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        product = item.product

        if item.quantity > product.stock:
            messages.error(
                request,
                f"Estoque insuficiente para {product.title}"
            )
            return redirect('orders:view_cart')




    if not cart_items.exists():
        return redirect('products:list')

    total_amount = sum(item.subtotal() for item in cart_items)

    cart = Cart.objects.filter(user=request.user).last()

    # Pedido principal
    order = Order.objects.create(
    cart=cart,
    status='created'
    )
    
    order.update_total()
    order.mark_paid()
    
    # Agrupar itens por vendedor
    vendor_map = {}

    for item in cart_items:
        order_item = OrderItem.objects.create(
            order=order,
            product=item.product,
            vendor=item.product.vendor,
            quantity=item.quantity,
            price=item.subtotal(),
            status='paid'
        )

        vendor_map.setdefault(item.product.vendor, []).append(order_item)

        # Atualiza estoque
        product = item.product
        product.stock = max(0, product.stock - item.quantity)
        product.save()

    # Criar repasses por vendedor
    for vendor, items in vendor_map.items():
        total_vendor = sum(i.price for i in items)
        
        #commission = total_vendor * 0.10  # 10% comissão
        commission = total_vendor * (product.category.marketplace_fee)/100  # comissão parametrizada na categoria

        payout = VendorPayout.objects.create(
            vendor=vendor,
            total_amount=total_vendor,
            commission=commission,
            status='pending'
        )
        payout.order_items.set(items)

    # Limpa carrinho
    cart_items.delete()

    return render(request, 'orders/checkout_success.html', {
        'order': order,
        'order_items': order.items.all()
    })


# ======================================================
# ADMIN / BACKOFFICE
# ======================================================

@login_required
def mark_order_paid(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    order.status = 'paid'.lower()
    order.save()

    # Atualiza itens
    for item in order.items.all():
        item.status = 'paid'
        item.save()

    # Atualiza payouts
    payouts = VendorPayout.objects.filter(
        order_items__order=order
    ).distinct()

    payouts.update(status='pending')

    return redirect('orders:view_cart')


# Remover um item do carrinho antes do Checkout final #
from django.shortcuts import redirect, get_object_or_404
from orders.models import OrderItem

@login_required
def remove_from_order(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, order__customer=request.user)
    item.delete()
    return redirect('orders:checkout')