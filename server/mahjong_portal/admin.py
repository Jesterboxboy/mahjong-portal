# -*- coding: utf-8 -*-

from django.contrib import admin

from mahjong_portal.models import SentEmail


@admin.register(SentEmail)
class SentEmailAdmin(admin.ModelAdmin):
    list_display = ["created_on", "subject", "to", "success"]
    list_filter = ["success", "created_on"]
    search_fields = ["subject", "to", "from_email", "body"]
    readonly_fields = [f.name for f in SentEmail._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
