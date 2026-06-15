# -*- coding: utf-8 -*-

from django.core.mail.backends.smtp import EmailBackend as SmtpEmailBackend


class DBLoggingEmailBackend(SmtpEmailBackend):
    """SMTP backend that also records every message in the SentEmail model."""

    def send_messages(self, email_messages):
        from mahjong_portal.models import SentEmail  # lazy import: apps must be loaded

        sent_count = 0
        # send one at a time so each message gets its own success/error record
        for message in email_messages:
            error = ""
            try:
                count = super().send_messages([message]) or 0
            except Exception as exc:  # noqa: BLE001 - record any send failure
                count = 0
                error = str(exc)

            # ponytail: stores body text only, not attachments. Upgrade: serialize alternatives/attachments if needed.
            SentEmail.objects.create(
                subject=message.subject or "",
                from_email=message.from_email or "",
                to=", ".join(message.to or []),
                cc=", ".join(getattr(message, "cc", []) or []),
                bcc=", ".join(getattr(message, "bcc", []) or []),
                body=message.body or "",
                success=bool(count),
                error=error,
            )
            sent_count += count

        return sent_count
