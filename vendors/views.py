from .models import Vendor
from datetime import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, When, Value, IntegerField
from django.db.models import F, DecimalField, ExpressionWrapper, Case, When, IntegerField
from django.db.models import F, ExpressionWrapper, DecimalField, Q
from django.db.models import Sum, Count, Q
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from orders.models import CartItem, Order, OrderItem, VendorPayout
from orders.models import OrderItem, Order
from products.models import Product
from products.models import Product, Category
from vendors.decorators import vendor_required
from vendors.forms import VendorForm
from vendors.models import Vendor


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

@login_required
def mark_order_paid(request, order_id):
    # Marca o pedido inteiro como pago manualmente
    order = get_object_or_404(Order, id=order_id)
    order.status = 'paid'
    order.save()

    # Atualiza todos os itens do pedido
    order_items = order.items.all()
    for item in order_items:
        item.status = 'paid'
        item.save()

    # Atualiza os VendorPayouts correspondentes
    payouts = VendorPayout.objects.filter(order_items__in=order_items).distinct()
    for payout in payouts:
        payout.status = 'pending'  # ainda não pago ao vendedor
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
    

# vendors/views.py
# vendor_orders:  Gestão de Pedidos do Vendedor
# O vendedor precisa ver apenas os pedidos que contêm seus produtos.
#====================================================================

@login_required
def vendor_orders(request):
    # Pega o vendedor logado
    vendor = get_object_or_404(Vendor, user=request.user)

    # Query dos pedidos do vendedor
    order_items = OrderItem.objects.filter(vendor=vendor).select_related(
        "order",
        "product",
        "order__billing_profile"
    ).annotate(
        total_price=ExpressionWrapper(
            F('quantity') * F('price'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        ),
        # Prioridade: itens pendentes (não enviados) vêm primeiro
        priority=Case(
            When(status='PENDING', then=1),
            When(status='PROCESSING', then=1),  # opcional, se houver outro status que significa "não enviado"
            default=2,  # itens já enviados
            output_field=IntegerField()
        )
    ).order_by('priority', '-order__created_at')  # Primeiro pendentes, depois históricos

    context = {
        "vendor": vendor,
        "order_items": order_items,
    }

    return render(request, "vendors/orders.html", context)


# vendors/views.py

# vendors/views.py







@login_required
def vendor_orders_dashboard(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    order_items = OrderItem.objects.filter(vendor=vendor).select_related(
        "order",
        "product",
        "product__category",
        "order__billing_profile"
    )

    # =================== FILTROS ===================
    status_filter = request.GET.get('status')
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    product_id = request.GET.get('product')
    category_id = request.GET.get('category')
    search = request.GET.get('search')  # pedido id ou email

    if status_filter:
        order_items = order_items.filter(status__iexact=status_filter)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            order_items = order_items.filter(order__created_at__range=[start, end])
        except ValueError:
            pass

    if product_id:
        order_items = order_items.filter(product__id=product_id)

    if category_id:
        order_items = order_items.filter(product__category__id=category_id)

    if search:
        order_items = order_items.filter(
            Q(order__order_id__icontains=search) |
            Q(order__billing_profile__email__icontains=search)
        )

    # =================== TOTAL PRICE ===================
    order_items = order_items.annotate(
        total_price=ExpressionWrapper(
            F('quantity') * F('price'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('status', '-order__created_at')  # pendentes primeiro

    # =================== ESTATÍSTICAS ===================
    total_orders = order_items.values('order').distinct().count()
    total_revenue = order_items.aggregate(total=Sum('total_price'))['total'] or 0
    pending_orders = order_items.filter(status='paid').count()
    shipped_orders = order_items.filter(status='shipped').count()

    context = {
        "vendor": vendor,
        "order_items": order_items,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "pending_orders": pending_orders,
        "shipped_orders": shipped_orders,
        "products": Product.objects.filter(vendor=vendor),
        "categories": Category.objects.all(),
        "status_filter": status_filter or "",
        "start_date": start_date or "",
        "end_date": end_date or "",
        "product_id": product_id or "",
        "category_id": category_id or "",
        "search": search or "",
    }

    return render(request, "vendors/orders_dashboard.html", context)

@login_required
def mark_item_shipped(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, vendor__user=request.user)
    item.status = 'SHIPPED'
    item.save()
    return redirect('vendors/orders_dashboard.html')  # ou o nome correto do seu dashboard


# Atualização do Estágio do Status
#====================================
# vendors/views.py

from orders.models import OrderItem, ORDER_STATUS_CHOICES

@login_required
def advance_order_status(request, item_id):
    status_flow = [s[0] for s in ORDER_STATUS_CHOICES]

    item = get_object_or_404(OrderItem, id=item_id, vendor__user=request.user)

    try:
        current_index = status_flow.index(item.status)
        if current_index < len(status_flow) - 1:
            item.status = status_flow[current_index + 1]
            item.save()
    except ValueError:
        item.status = 'created'
        item.save()

    return redirect('vendors:vendor_orders_dashboard')

@login_required
def cancel_order_item(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id, vendor__user=request.user)

    # Só permite cancelar se ainda não enviado
    if item.status not in ['shipped', 'refunded']:
        item.status = 'refunded'  # ou 'canceled' se preferir
        item.save()

    return redirect('vendors:vendor_orders_dashboard')