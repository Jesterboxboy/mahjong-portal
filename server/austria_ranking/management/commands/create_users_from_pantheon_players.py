# -*- coding: utf-8 -*-
"""
Management command: create_users_from_pantheon_players

For all Player records (filtered to country=AT by default) that have a
pantheon_id set, calls Frey GetPersonalInfo to retrieve their email address
and creates a Django User account with attached_player already linked.

Frey only returns email addresses to superadmin callers. You must supply
Pantheon superadmin credentials via --admin-email / --admin-password arguments
or via the PANTHEON_ADMIN_EMAIL / PANTHEON_ADMIN_PASSWORD environment variables.

Players whose pantheon_id already has a corresponding User are skipped.

Requires settings.PANTHEON_AUTH_API_URL to be configured.

Usage:
    python manage.py create_users_from_pantheon_players --admin-email admin@example.com --admin-password secret
    python manage.py create_users_from_pantheon_players --admin-email admin@example.com --admin-password secret --dry-run
    python manage.py create_users_from_pantheon_players --admin-email admin@example.com --admin-password secret --all-countries
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from twirp.context import Context
from twirp.exceptions import TwirpServerException

from account.models import User
from pantheon_api import frey_pb2
from pantheon_api.frey_twirp import FreyClient
from player.models import Player


class Command(BaseCommand):
    help = (
        "Create Django User accounts for Player records that have a pantheon_id, "
        "fetching email from Frey (as superadmin) and linking attached_player automatically."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--admin-email",
            default=os.environ.get("PANTHEON_ADMIN_EMAIL", ""),
            help="Pantheon superadmin email. Falls back to PANTHEON_ADMIN_EMAIL env var.",
        )
        parser.add_argument(
            "--admin-password",
            default=os.environ.get("PANTHEON_ADMIN_PASSWORD", ""),
            help="Pantheon superadmin password. Falls back to PANTHEON_ADMIN_PASSWORD env var.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print actions without writing to the database.",
        )
        parser.add_argument(
            "--all-countries",
            action="store_true",
            default=False,
            help="Process players from all countries, not just AT.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        all_countries: bool = options["all_countries"]
        admin_email: str = options["admin_email"]
        admin_password: str = options["admin_password"]

        if not getattr(settings, "PANTHEON_AUTH_API_URL", None):
            raise CommandError(
                "settings.PANTHEON_AUTH_API_URL is not configured. "
                "Set the PANTHEON_AUTH_API_URL environment variable and retry."
            )

        if not admin_email or not admin_password:
            raise CommandError(
                "Pantheon superadmin credentials required. "
                "Pass --admin-email and --admin-password, or set "
                "PANTHEON_ADMIN_EMAIL and PANTHEON_ADMIN_PASSWORD environment variables."
            )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be written."))

        client = FreyClient(settings.PANTHEON_AUTH_API_URL)

        # Authenticate as superadmin — email is only returned for superadmin callers
        self.stdout.write(f"Authenticating as superadmin ({admin_email})…")
        try:
            auth = client.Authorize(
                ctx=Context(),
                request=frey_pb2.AuthAuthorizePayload(email=admin_email, password=admin_password),
                server_path_prefix="/v2",
                timeout=15,
            )
        except TwirpServerException as exc:
            raise CommandError(f"Pantheon authentication failed: {exc}") from exc

        admin_ctx = Context(
            headers={
                "X-Current-Person-Id": str(auth.person_id),
                "X-Auth-Token": auth.auth_token,
            }
        )
        self.stdout.write(self.style.SUCCESS(f"Authenticated as person_id={auth.person_id}.\n"))

        qs = Player.objects.filter(pantheon_id__isnull=False)
        if not all_countries:
            qs = qs.filter(country__code="AT")

        # Exclude players that already have a linked User
        existing_pantheon_ids = set(
            User.objects.filter(new_pantheon_id__isnull=False).values_list("new_pantheon_id", flat=True)
        )

        players = [p for p in qs.order_by("last_name", "first_name") if p.pantheon_id not in existing_pantheon_ids]
        already_have_user = qs.count() - len(players)

        self.stdout.write(
            f"Found {qs.count()} player(s) with pantheon_id — "
            f"{already_have_user} already have a User, {len(players)} to process.\n"
        )

        if not players:
            self.stdout.write("Nothing to do.")
            return

        # Fetch all Frey PersonEx records in one batched call using superadmin auth
        pantheon_ids = [p.pantheon_id for p in players]
        try:
            response = client.GetPersonalInfo(
                ctx=admin_ctx,
                request=frey_pb2.PersonsGetPersonalInfoPayload(ids=pantheon_ids),
                server_path_prefix="/v2",
                timeout=30,
            )
        except TwirpServerException as exc:
            raise CommandError(f"Frey GetPersonalInfo failed: {exc}") from exc

        person_by_id = {person.id: person for person in response.people}

        created = 0
        skipped = 0

        for player in players:
            person = person_by_id.get(player.pantheon_id)

            if person is None:
                self.stdout.write(
                    self.style.WARNING(f"  NO FREY DATA  {player} (pantheon_id={player.pantheon_id}) — skipping")
                )
                skipped += 1
                continue

            email = person.email
            if not email:
                self.stdout.write(
                    self.style.WARNING(
                        f"  NO EMAIL  {player} (pantheon_id={player.pantheon_id}, Frey {person.title!r}) — skipping"
                    )
                )
                skipped += 1
                continue

            if dry_run:
                self.stdout.write(
                    f"  WOULD CREATE  User({email}) → Player {player!r} (pantheon_id={player.pantheon_id})"
                )
                created += 1
                continue

            try:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=None,
                )
                user.new_pantheon_id = player.pantheon_id
                user.attached_player = player
                user.save(update_fields=["new_pantheon_id", "attached_player"])
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  CREATED  User({email}) → Player {player!r} (pantheon_id={player.pantheon_id})"
                    )
                )
                created += 1
            except IntegrityError:
                # username (email) already taken by a different account
                self.stdout.write(
                    self.style.WARNING(
                        f"  DUPLICATE EMAIL  {email} already exists as a username — skipping Player {player!r}"
                    )
                )
                skipped += 1

        action = "Would create" if dry_run else "Created"
        self.stdout.write(self.style.SUCCESS(f"\nDone. {action} {created} user(s), skipped {skipped}."))
