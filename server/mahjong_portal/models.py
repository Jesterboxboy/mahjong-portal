# -*- coding: utf-8 -*-

from django.db import models


class BaseModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.__unicode__()


class SentEmail(models.Model):
    """Log of every email sent through DBLoggingEmailBackend, for admin review."""

    created_on = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=998, blank=True)
    from_email = models.CharField(max_length=254, blank=True)
    to = models.TextField(blank=True)
    cc = models.TextField(blank=True)
    bcc = models.TextField(blank=True)
    body = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    error = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_on"]

    def __str__(self):
        return f"{self.created_on:%Y-%m-%d %H:%M} {self.subject} -> {self.to}"
