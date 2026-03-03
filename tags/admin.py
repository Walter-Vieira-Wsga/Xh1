from django.contrib import admin
from .models import Tag


class TagsAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug',]  # remove 'slug'

admin.site.register(Tag, TagsAdmin)
