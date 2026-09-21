# -*- coding: utf-8 -*-

from django.db import models

from mahjong_portal.models import BaseModel


class Country(BaseModel):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class City(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]

    def __unicode__(self):
        return self.name


class FreyConnector(BaseModel):
    """Singleton holding the Pantheon admin credentials the portal acts with.

    Only the token is stored: Frey derives it from the password, so a stored password
    would go stale on the same reset that kills the token.
    """

    email = models.EmailField(blank=True)
    person_id = models.PositiveIntegerField(null=True, blank=True)
    auth_token = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Frey connector"
        verbose_name_plural = "Frey connector"

    def __unicode__(self):
        return "Frey connector"

    @classmethod
    def credentials(cls):
        """(person_id, auth_token), falling back to the env settings when not configured here."""
        from django.conf import settings

        connector = cls.objects.first()
        if connector and connector.auth_token and connector.person_id:
            return connector.person_id, connector.auth_token
        return settings.PANTHEON_ADMIN_ID, settings.PANTHEON_ADMIN_COOKIE


def pantheon_admin_id():
    return FreyConnector.credentials()[0]


def pantheon_admin_token():
    return FreyConnector.credentials()[1]
