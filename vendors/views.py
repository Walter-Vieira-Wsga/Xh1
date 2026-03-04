from orders.models import CartItem, Order, OrderItem, VendorPayout
from products.models import Product
from vendors.models import Vendor
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from vendors.forms import VendorForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from vendors.decorators import vendor_required
from orders.models import OrderItem
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from products.models import Product


@login_required
def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum([item.subtotal() for item in cart_items])
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def remove_from_cart(request, item_id):
    item = CartItem.objects.get(id=item_id, user=request.user)
    item.delete()
    return redirect('view_cart')    



# Checkout e Criação de Pedidos
#========================================================================#
@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect('product_list')

    total_amount = sum([item.subtotal() for item in cart_items])

    # Criar pedido geral
    order = Order.objects.create(
        customer=request.user,
        total_amount=total_amount,
        status='PENDING',
        payment_method='PIX/Stripe'  # placeholder
    )

    # Criar OrderItems e VendorPayouts
    vendor_dict = {}
    for item in cart_items:
        order_item = OrderItem.objects.create(
            order=order,
            product=item.product,
            vendor=item.product.vendor,
            quantity=item.quantity,
            price=item.subtotal(),
            status='PENDING'
        )
        # Organizar por vendedor para VendorPayout
        if item.product.vendor not in vendor_dict:
            vendor_dict[item.product.vendor] = []
        vendor_dict[item.product.vendor].append(order_item)
        # Atualizar estoque
        item.product.stock -= item.quantity
        item.product.save()

    # Criar registros de pagamento para cada vendedor
    for vendor, items in vendor_dict.items():
        total_vendor = sum([oi.price for oi in items])
        commission = total_vendor * 0.1  # Exemplo: 10% comissão
        payout = VendorPayout.objects.create(
            vendor=vendor,
            total_amount=total_vendor,
            commission=commission,
            status='PENDING'
        )
        payout.order_items.set(items)

    # Limpar carrinho
    cart_items.delete()

    return render(request, 'orders/checkout_success.html', {'order': order})

# Atualização de Pedidos como "Pago" Manualmente
#========================================================================#
from django.shortcuts import render, redirect, get_object_or_404
from orders.models import Order, OrderItem, VendorPayout
from django.contrib.auth.decorators import login_required

@login_required
def mark_order_paid(request, order_id):
    # Marca o pedido inteiro como pago manualmente
    order = get_object_or_404(Order, id=order_id)
    order.status = 'PAID'
    order.save()

    # Atualiza todos os itens do pedido
    order_items = order.items.all()
    for item in order_items:
        item.status = 'PAID'
        item.save()

    # Atualiza os VendorPayouts correspondentes
    payouts = VendorPayout.objects.filter(order_items__in=order_items).distinct()
    for payout in payouts:
        payout.status = 'PENDING'  # ainda não pago ao vendedor
        payout.save()

    return redirect('view_order', order_id=order.id)



# ==================================================
# REGISTRO DE VENDEDOR
# ==================================================
@login_required
def vendor_register(request):
    # Se já for vendedor, vai direto pro dashboard
    if hasattr(request.user, 'vendor'):
        return redirect('vendors:vendor_dashboard')

    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            return redirect('vendors:vendor_dashboard')
    else:
        form = VendorForm()

    return render(request, 'vendors/vendor_register.html', {'form': form})


# ==================================================
# DASHBOARD DO VENDEDOR
# ==================================================

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from orders.models import OrderItem, VendorPayout
from django.db.models import Sum, F
from datetime import datetime

@login_required
def vendor_dashboard(request):
    vendor = request.user.vendor  # assume que User tem FK para Vendor

    # Filtro por período (GET parameters)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')

    order_items = OrderItem.objects.filter(vendor=vendor, order__status='paid')

    if start_date and end_date:
        # converte strings para datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        order_items = order_items.filter(order__created_at__range=[start_dt, end_dt])

    # Total por produto
    sales_by_product = (
        order_items
        .values('product__name')
        .annotate(
            total_quantity=Sum('quantity'),
            total_revenue=Sum(F('quantity')*F('price'))
        )
        .order_by('-total_revenue')
    )

    # Total geral
    total_sales = sum(item['total_revenue'] for item in sales_by_product)

    # Status de repasse
    payouts = VendorPayout.objects.filter(vendor=vendor).order_by('-created_at')

    context = {
        'sales_by_product': sales_by_product,
        'total_sales': total_sales,
        'payouts': payouts,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'vendors/dashboard.html', context)

# ==================================================
# LOGIN DO VENDEDOR
# ==================================================
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from vendors.models import Vendor

def vendor_login(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'vendor'):
            return redirect('vendors:vendor_dashboard')
        else:
            return redirect('vendors:vendor_register')

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('vendors:vendor_dashboard')

    return render(request, "vendors/login.html")



def vendor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('vendors:vendor_login')

        if not hasattr(request.user, 'vendor'):
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return wrapper



class VendorProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "vendors/vendor_product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(
            vendor=self.request.user.vendor
        ).order_by('-id')
    