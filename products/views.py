from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DeleteView
from django.urls import reverse_lazy
from products.forms import ProductForm
from django.db.models import Prefetch
from products.models import Product, Category, ProductImage
from django.contrib.auth.mixins import LoginRequiredMixin

# Listagem de produtos ativos
class ProductListView(ListView):
    model = Product

    def get_queryset(self):
        return Product.objects.prefetch_related(
            Prefetch(
                "images",
                queryset=ProductImage.objects.filter(is_main=True),
                to_attr="main_images"
            )
        )

# Detalhes do produto via slug
class ProductDetailSlugView(DetailView):
    model = Product
    template_name = "products/detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        return get_object_or_404(Product, slug=slug, active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["related_products"] = Product.objects.filter(
            category=self.object.category,
            active=True
        ).exclude(id=self.object.id)[:4]

        return context

# Criar produto (só para vendedores logados)
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProductForm
from .models import ProductImage

class ProductCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = ProductForm()
        formset = ProductImageFormSet(prefix='images')
        return render(request, 'products/product_form.html', {
            'form': form,
            'formset': formset
        })

    def post(self, request):
        form = ProductForm(request.POST)
        formset = ProductImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()

            formset.instance = product
            formset.save()

            return redirect('vendors:vendor_dashboard')

        return render(request, 'products/product_form.html', {
            'form': form,
            'formset': formset
        })
        
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ProductImageFormSet

class ProductImageManageView(LoginRequiredMixin, View):
    template_name = 'products/product_images_manage.html'

    def get(self, request, pk):
        product = get_object_or_404(
            Product,
            pk=pk,
            vendor=request.user.vendor
        )
        formset = ProductImageFormSet(instance=product)
        return render(request, self.template_name, {
            'product': product,
            'formset': formset
        })

    def post(self, request, pk):
        product = get_object_or_404(
            Product,
            pk=pk,
            vendor=request.user.vendor
        )
        formset = ProductImageFormSet(
            request.POST,
            request.FILES,
            instance=product
        )

        if formset.is_valid():
            formset.save()
            return redirect('vendors:vendor_dashboard')

        return render(request, self.template_name, {
            'product': product,
            'formset': formset
        })    

from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Product
from .forms import ProductForm

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_form_edit.html"

    def get_queryset(self):
        # garante que o vendedor só edite produtos dele
        return Product.objects.filter(
            vendor=self.request.user.vendor
        )

    def get_success_url(self):
        return reverse_lazy('vendors:vendor_products')

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy('vendors:vendor_products')

    def get_queryset(self):
        return Product.objects.filter(vendor__user=self.request.user)       
    
    