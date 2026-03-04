from django.views.generic import ListView
from products.models import Product
from .models import Tag

class TagDetailView(ListView):
    model = Product
    template_name = 'tags/tag_detail.html'
    context_object_name = 'products'
    paginate_by = 12  # opcional: paginação

    def get_queryset(self):
        self.tag = Tag.objects.get(slug=self.kwargs['slug'])
        return self.tag.products.filter(active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context