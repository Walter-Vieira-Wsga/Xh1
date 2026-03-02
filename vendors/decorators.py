from django.shortcuts import redirect
from vendors.models import Vendor

def vendor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('vendors:vendor_login')
        try:
            request.user.vendor
        except Vendor.DoesNotExist:
            return redirect('vendors:vendor_login')
        return view_func(request, *args, **kwargs)
    return wrapper