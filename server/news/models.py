# -*- coding: utf-8 -*-

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from filebrowser.fields import FileBrowseField


class NewsArticle(models.Model):
    NEWS = "news"
    EVENT = "veranstaltung"

    CATEGORY_CHOICES = [
        (NEWS, "News"),
        (EVENT, "Veranstaltung"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True, default="")
    body = models.TextField(blank=True, default="")
    image = FileBrowseField(
        _("Image (from media library)"),
        max_length=200,
        directory="news/",
        extensions=[".jpg", ".jpeg", ".png", ".gif", ".webp"],
        null=True,
        blank=True,
    )
    published_date = models.DateField()
    is_published = models.BooleanField(default=False)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=NEWS)

    class Meta:
        ordering = ["-published_date"]
        verbose_name = "News Article"
        verbose_name_plural = "News Articles"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
