from django.shortcuts import render
from vendors.models import Vendor
from django.db.models import Sum, Count,F 
from django.contrib.auth.decorators import login_required
from orders.models import OrderItem, VendorPayout
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
@login_required
def sales_report(request):

    order_items = OrderItem.objects.filter(order__status='paid')

    # ========================
    # FILTROS
    # ========================

    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    vendor_id = request.GET.get('vendor')

    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        order_items = order_items.filter(order__created_at__range=[start, end])

    if vendor_id:
        order_items = order_items.filter(vendor__id=vendor_id)

    # ========================
    # ANOTAÇÕES
    # ========================

    order_items = order_items.annotate(
        order_code=F('order__order_id'),
        order_date=F('order__created_at'),
        shipping_total=F('order__shipping_total'),
        product_name=F('product__name'),
        vendor_name = F('vendor__company_name'),
        item_total=F('quantity') * F('price')
    ).order_by('-order_date')

    # ========================
    # TOTAIS GERAIS
    # ========================

    totals = order_items.aggregate(
        total_revenue=Sum(F('quantity') * F('price')),
        total_shipping=Sum('order__shipping_total')
    )

    total_revenue = totals['total_revenue'] or 0
    total_shipping = totals['total_shipping'] or 0

    # ========================
    # COMISSÕES (Marketplace)
    # ========================

    payouts = VendorPayout.objects.all()
    total_commission = payouts.aggregate(
        total=Sum('commission')
    )['total'] or 0

    context = {
        'order_items': order_items,
        'vendors': Vendor.objects.all(),
        'total_revenue': total_revenue,
        'total_shipping': total_shipping,
        'total_commission': total_commission,
        'start_date': start_date,
        'end_date': end_date,
        'vendor_id': vendor_id,
    }

    return render(request, 'reports/sales_report.html', context)    