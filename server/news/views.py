# -*- coding: utf-8 -*-

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from news.models import NewsArticle


def news_list(request):
    articles = NewsArticle.objects.filter(is_published=True)
    paginator = Paginator(articles, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "news/list.html", {"page": "news", "page_obj": page_obj})


def news_detail(request, slug):
    article = get_object_or_404(NewsArticle, slug=slug, is_published=True)
    return render(request, "news/detail.html", {"page": "news", "article": article})
