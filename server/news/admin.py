# -*- coding: utf-8 -*-

from django.contrib import admin
from tinymce.widgets import TinyMCE

from news.models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "published_date", "is_published"]
    list_filter = ["is_published", "category"]
    search_fields = ["title", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"
    ordering = ["-published_date"]
    fieldsets = (
        (None, {
            "fields": ("title", "slug", "category", "published_date", "is_published")
        }),
        ("Content", {
            "fields": ("excerpt", "body", "image")
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields["excerpt"].widget = TinyMCE()
        form.base_fields["body"].widget = TinyMCE()
        return form
