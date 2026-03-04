from django.urls import path
from reports import views
from .views import sales_report

app_name = "reports"

urlpatterns = [
    path('vendor/', views.vendor_report, name='vendor_report'),
    path('sales/', sales_report, name='sales_report'),
]
