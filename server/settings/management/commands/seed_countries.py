# -*- coding: utf-8 -*-

import pytz
from django.core.management.base import BaseCommand

from settings.models import Country


class Command(BaseCommand):
    help = "Fill the Country table with the ISO 3166 list shipped in pytz. Existing rows keep their name."

    def handle(self, *args, **options):
        created = 0
        for code, name in pytz.country_names.items():
            _, was_created = Country.objects.get_or_create(code=code, defaults={"name": name})
            created += was_created

        self.stdout.write(f"countries added: {created}, total: {Country.objects.count()}")
