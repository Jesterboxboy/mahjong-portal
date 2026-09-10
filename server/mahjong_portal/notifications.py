# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import EmailMessage
from django.urls import reverse

logger = logging.getLogger(__name__)


def _admin_url(obj):
    """Best-effort absolute URL to an object's admin change page."""
    meta = obj._meta
    path = reverse(f"admin:{meta.app_label}_{meta.model_name}_change", args=[obj.pk])
    try:
        domain = Site.objects.get_current().domain
    except Exception:  # noqa: BLE001
        domain = (settings.ALLOWED_HOSTS or ["localhost"])[0]
    return f"{settings.SCHEME}://{domain}{path}"


def notify_superusers_attach_request(attach_request):
    """Email all superusers when a player-attach request is created."""
    from account.models import User

    recipients = list(User.objects.filter(is_superuser=True).exclude(email="").values_list("email", flat=True))
    if not recipients:
        return

    subject = "New player attach request"
    body = (
        f"User {attach_request.user!r} requested to be attached to player "
        f"{attach_request.player!r}.\n\n"
        f"Contacts provided:\n{attach_request.contacts}\n\n"
        f"Review: {_admin_url(attach_request)}"
    )
    _send(subject, body, recipients)


def notify_organizers_new_registration(registration):
    """Email a tournament's organizer addresses when a new registration is created."""
    recipients = registration.tournament.get_organizer_emails()
    if not recipients:
        return

    name = f"{registration.first_name} {registration.last_name}".strip()
    contact = getattr(registration, "contact", None) or getattr(registration, "email", "") or ""
    subject = f"New registration: {registration.tournament.name}"
    body = (
        f"A new registration was submitted for {registration.tournament.name!r}.\n\n"
        f"Name: {name}\n"
        f"City: {registration.city}\n"
        f"Contact: {contact}\n"
        f"Approved: {registration.is_approved}\n"
    )
    _send(subject, body, recipients)


def notify_pantheon_sync_failure(registration, reason):
    """Email organizers and superusers when a registrant could not be pushed to Pantheon."""
    from account.models import User

    tournament = registration.tournament
    recipients = tournament.get_organizer_emails()
    recipients += list(User.objects.filter(is_superuser=True).exclude(email="").values_list("email", flat=True))
    if not recipients:
        return

    name = f"{registration.first_name} {registration.last_name}".strip()
    subject = f"Pantheon registration failed: {tournament.name}"
    body = (
        f"{name!r} was approved for {tournament.name!r} but could NOT be added to the "
        f"linked Pantheon event (id {tournament.new_pantheon_id}).\n\n"
        f"Reason: {reason}\n\n"
        f"The portal registration was kept. Please add the player in Pantheon manually, "
        f"or retry from the admin.\n\n"
        f"Registration: {_admin_url(registration)}"
    )
    _send(subject, body, recipients)


def _fill(text, registration):
    # plain placeholder substitution only — no template engine, no SSTI surface
    return (
        (text or "")
        .replace("{{first_name}}", registration.first_name or "")
        .replace("{{last_name}}", registration.last_name or "")
    )


def _render(template, registration):
    """Render a TournamentEmailTemplate's subject/body with the registrant's name."""
    return _fill(template.subject, registration), _fill(template.body, registration)


def confirmation_email(registration):
    """Send the tournament's confirmation template to a registrant who became approved."""
    from tournament.models import TournamentEmailTemplate

    template = registration.tournament.email_templates.filter(email_type=TournamentEmailTemplate.CONFIRMATION).first()
    if not template:
        return

    recipient = registration.get_recipient_email()
    if not recipient:
        return

    subject, body = _render(template, registration)
    _send(subject, body, [recipient], reply_to=template.reply_to)


def registrant_email(tournament):
    """Send the tournament's registrant template to all approved players. Returns count sent."""
    from tournament.models import TournamentEmailTemplate

    template = tournament.email_templates.filter(email_type=TournamentEmailTemplate.REGISTRANT).first()
    if not template:
        return 0

    sent = 0
    for registration in tournament.get_tournament_registrations():
        recipient = registration.get_recipient_email()
        if not recipient:
            continue
        subject, body = _render(template, registration)
        _send(subject, body, [recipient], reply_to=template.reply_to)
        sent += 1
    return sent


def _send(subject, body, recipients, reply_to=None):
    # never let a mail failure break the user's request flow
    try:
        message = EmailMessage(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            recipients,
            reply_to=[reply_to] if reply_to else None,
        )
        message.send(fail_silently=False)
    except Exception:  # noqa: BLE001
        logger.exception("Failed to send notification email: %s", subject)
