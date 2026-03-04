from django.urls import path
from .views import TagDetailView

app_name = "tags"

urlpatterns = [
    path('<slug:slug>/', TagDetailView.as_view(), name='tag_detail'),
]