from django.shortcuts import render
from vendors.models import Vendor
from django.db.models import Sum, Count,F 
from django.contrib.auth.decorators import login_required
from orders.models import OrderItem, VendorPayout, Order
from datetime import datetime





@login_required
def vendor_report(request):
    vendor = request.user.vendor

    # Total de vendas realizadas (entregues)
    total_sales = OrderItem.objects.filter(vendor=vendor, status='DELIVERED') \
                                   .aggregate(total=Sum('price'))['total'] or 0

    # Total de pedidos
    total_orders = OrderItem.objects.filter(vendor=vendor).count()

    # Produtos sem estoque
    out_of_stock = vendor.product_set.filter(stock__lte=0).count()

    # Total de VendorPayout pendentes
    pending_payouts = vendor.vendorpayout_set.filter(status='PENDING') \
                                             .aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'out_of_stock': out_of_stock,
        'pending_payouts': pending_payouts
    }

    return render(request, 'reports/vendor_report.html', context)



# Relatório de Vendas Efetuadas #
from django.db.models import Subquery, OuterRef, DecimalField



@login_required
def sales_report(request):

    order_items = OrderItem.objects.filter(status='paid')

    # filtros
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    vendor_id = request.GET.get('vendor')

    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        order_items = order_items.filter(order__created_at__range=[start, end])

    if vendor_id:
        order_items = order_items.filter(vendor__id=vendor_id)

    # anotações
    order_items = order_items.annotate(
        order_code=F('order__order_id'),
        order_date=F('order__created_at'),
        shipping_total=F('order__shipping_total'),
        product_name=F('product__name'),
        vendor_name=F('vendor__company_name'),
        item_total=F('quantity') * F('price'),

        # comissão
        commission=Sum('vendorpayout__commission'),

        # lucro vendedor
        vendor_profit=(F('quantity') * F('price')) - Sum('vendorpayout__commission')
    ).order_by('-order_date')

    # faturamento total
    total_revenue = order_items.aggregate(
        total=Sum(F('quantity') * F('price'))
    )['total'] or 0

    # frete total
    paid_orders = Order.objects.filter(status='paid')

    total_shipping = paid_orders.aggregate(
        total=Sum('shipping_total')
    )['total'] or 0

    # total comissão marketplace
    total_commission = VendorPayout.objects.aggregate(
        total=Sum('commission')
    )['total'] or 0

    # produtos mais vendidos
    top_products = (
        OrderItem.objects
        .filter(status='paid')
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:10]
    )

    # vendas por vendedor
    sales_by_vendor = (
        OrderItem.objects
        .filter(status='paid')
        .values('vendor__company_name')
        .annotate(total_sales=Sum(F('quantity') * F('price')))
        .order_by('-total_sales')
    )

    context = {
        'order_items': order_items,
        'vendors': Vendor.objects.all(),
        'total_revenue': total_revenue,
        'total_shipping': total_shipping,
        'total_commission': total_commission,
        'top_products': top_products,
        'sales_by_vendor': sales_by_vendor,
        'start_date': start_date,
        'end_date': end_date,
        'vendor_id': vendor_id,
    }

    return render(request, 'reports/sales_report.html', context)