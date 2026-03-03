from django.urls import path
from .views import ProductListView, ProductDetailSlugView, ProductCreateView, ProductImageManageView, ProductUpdateView, ProductDeleteView

app_name = "products"

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),

    # ⚠️ rotas específicas PRIMEIRO
    path('product/<int:pk>/images/', ProductImageManageView.as_view(), name='product_images_manage'),

    # ⚠️ slug SEMPRE por último
    path('<slug:slug>/', ProductDetailSlugView.as_view(), name='product_detail'),

    # ⚠️ Altera dados do Produto
    path('edit/<int:pk>/', ProductUpdateView.as_view(), name='product_edit'),
    
    # ⚠️ Deletar dados do Produto
    path("products/<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
]    

