# -*- coding: utf-8 -*-

from django.contrib import admin
from django.utils.html import format_html

from news.models import NewsArticle


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "published_date", "is_published", "image_preview"]
    list_filter = ["is_published", "category"]
    search_fields = ["title", "excerpt"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"
    ordering = ["-published_date"]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 40px;" />', obj.image)
        return "-"

    image_preview.short_description = "Vorschau"
