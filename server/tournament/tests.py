# -*- coding: utf-8 -*-

import datetime
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from account.models import User
from settings.models import Country
from tournament.forms import TournamentRegistrationForm
from tournament.models import Tournament, TournamentRegistration
from utils.general import split_name


class SplitNameTest(TestCase):
    """Pantheon stores names in western order: given names first, surname last."""

    def test_middle_names_go_to_first_name(self):
        self.assertEqual(split_name("Michael Mike Gürtl-Dusleag"), ("Michael Mike", "Gürtl-Dusleag"))

    def test_two_part_name(self):
        self.assertEqual(split_name("Hans Müller"), ("Hans", "Müller"))

    def test_single_word_name(self):
        self.assertEqual(split_name("Mike"), ("Mike", ""))


@override_settings(PANTHEON_ADMIN_ID=1)
class OfflinePantheonRegistrationTest(TestCase):
    def setUp(self):
        country = Country.objects.create(code="AT", name="Austria")
        self.tournament = Tournament.objects.create(
            name="Offline Pantheon Cup",
            slug="offline-pantheon-cup",
            end_date=datetime.date(2026, 1, 1),
            country=country,
            is_pantheon_registration=True,
            new_pantheon_id="42",
        )
        self.user = User.objects.create_user(username="p@example.com", email="p@example.com", password=None)
        self.user.new_pantheon_id = 777
        self.user.save()

    def _registration(self, **kwargs):
        return TournamentRegistration.objects.create(
            tournament=self.tournament,
            user=self.user,
            first_name="Hans",
            last_name="Müller",
            city="Wien",
            email="p@example.com",
            is_approved=False,
            **kwargs,
        )

    def test_pushed_once_on_approval_and_not_again(self):
        registration = self._registration()

        with patch("utils.new_pantheon.register_player") as register:
            registration.is_approved = True
            registration.save()
            register.assert_called_once_with(1, "42", 777)

            # a second save must not push again — pantheon_synced_on short-circuits it
            registration.save()
            self.assertEqual(register.call_count, 1)

        registration.refresh_from_db()
        self.assertIsNotNone(registration.pantheon_synced_on)
        self.assertEqual(registration.pantheon_sync_error, "")

    def test_failure_keeps_registration_and_records_error(self):
        registration = self._registration()

        with patch("utils.new_pantheon.register_player", side_effect=RuntimeError("pantheon is down")):
            registration.is_approved = True
            registration.save()

        registration.refresh_from_db()
        self.assertTrue(registration.is_approved)
        self.assertIsNone(registration.pantheon_synced_on)
        self.assertIn("pantheon is down", registration.pantheon_sync_error)

    def _confirmation_template(self):
        from tournament.models import TournamentEmailTemplate

        self.tournament.organizer_emails = "organizer@example.com"
        self.tournament.save()
        return TournamentEmailTemplate.objects.create(
            tournament=self.tournament,
            email_type=TournamentEmailTemplate.CONFIRMATION,
            subject="Welcome {{first_name}}",
            body="You are registered.",
        )

    def _recipients(self):
        return [address for message in mail.outbox for address in message.to]

    def test_failed_push_emails_only_the_admins(self):
        self._confirmation_template()
        registration = self._registration()

        with patch("utils.new_pantheon.register_player", side_effect=RuntimeError("pantheon is down")):
            registration.is_approved = True
            registration.save()

        self.assertEqual(self._recipients(), ["organizer@example.com"])

    def test_successful_push_emails_the_registrant(self):
        self._confirmation_template()
        registration = self._registration()

        with patch("utils.new_pantheon.register_player"):
            registration.is_approved = True
            registration.save()

        self.assertIn(registration.email, self._recipients())

    def test_retry_action_sends_the_withheld_confirmation(self):
        from unittest.mock import MagicMock

        from tournament.admin import retry_pantheon_registration

        self._confirmation_template()
        registration = self._registration()
        with patch("utils.new_pantheon.register_player", side_effect=RuntimeError("pantheon is down")):
            registration.is_approved = True
            registration.save()
        mail.outbox = []

        with patch("utils.new_pantheon.register_player"):
            retry_pantheon_registration(MagicMock(), None, TournamentRegistration.objects.all())

        self.assertIn(registration.email, self._recipients())

    def test_attached_player_wins_over_name_matching(self):
        """A Pantheon title with a middle name defeats find_player_smart; the account link must win."""
        from player.models import Player
        from player.player_helper import PlayerHelper

        player = Player.objects.create(first_name="Michael", last_name="Gürtl-Dusleag", slug="michael-guertl")
        self.user.attached_player = player
        self.user.save()

        self.assertIsNone(PlayerHelper.find_player_smart("Michael Mike Gürtl-Dusleag"))
        self.assertEqual(self.user.attached_player, player)

    def test_online_tournament_is_not_pushed(self):
        self.tournament.tournament_games_type = Tournament.ONLINE_GAMES
        self.tournament.save()
        registration = self._registration()

        with patch("utils.new_pantheon.register_player") as register:
            registration.is_approved = True
            registration.save()
            register.assert_not_called()


class EntryFeeTest(TestCase):
    def setUp(self):
        country = Country.objects.create(code="AT", name="Austria")
        self.paid_cup = self._tournament("paid-cup", country, entry_fee=True)
        self.free_cup = self._tournament("free-cup", country, entry_fee=False)

    @staticmethod
    def _tournament(slug, country, **kwargs):
        return Tournament.objects.create(
            name=slug, slug=slug, end_date=datetime.date(2026, 1, 1), country=country, is_upcoming=True, **kwargs
        )

    @staticmethod
    def _registration(tournament, **kwargs):
        return TournamentRegistration.objects.create(
            tournament=tournament, first_name="Hans", last_name="Müller", city="Wien", email="h@example.com", **kwargs
        )

    def test_action_marks_only_entry_fee_tournaments(self):
        from unittest.mock import MagicMock

        from tournament.admin import mark_as_paid

        paid = self._registration(self.paid_cup)
        free = self._registration(self.free_cup)

        mark_as_paid(MagicMock(), None, TournamentRegistration.objects.all())

        paid.refresh_from_db()
        free.refresh_from_db()
        self.assertTrue(paid.has_paid)
        self.assertFalse(free.has_paid)

    def test_paid_column_only_with_entry_fee(self):
        self._registration(self.paid_cup, has_paid=True)
        self._registration(self.free_cup, has_paid=True)

        with_fee = self.client.get(self.paid_cup.get_url()).content.decode()
        without_fee = self.client.get(self.free_cup.get_url()).content.decode()

        self.assertIn('class="text-success"', with_fee)
        self.assertNotIn('class="text-success"', without_fee)

    def test_dan_column_only_with_show_online_rank(self):
        self._registration(self.paid_cup)
        self.assertNotIn('<th scope="col">Dan</th>', self.client.get(self.paid_cup.get_url()).content.decode())

        self.paid_cup.show_online_rank = True
        self.paid_cup.save()
        self.assertIn('<th scope="col">Dan</th>', self.client.get(self.paid_cup.get_url()).content.decode())


class PendingRegistrationsCountTest(TestCase):
    def setUp(self):
        country = Country.objects.create(code="AT", name="Austria")
        self.tournament = Tournament.objects.create(
            name="moderated-cup",
            slug="moderated-cup",
            end_date=datetime.date(2026, 1, 1),
            country=country,
            is_upcoming=True,
            registrations_pre_moderation=True,
        )

    def _registration(self, **kwargs):
        return TournamentRegistration.objects.create(
            tournament=self.tournament,
            first_name="Hans",
            last_name="Müller",
            city="Wien",
            email="h@example.com",
            **kwargs,
        )

    def test_counts_only_unapproved(self):
        self._registration(is_approved=False)
        self._registration(is_approved=False)
        self._registration(is_approved=True)

        self.assertEqual(self.tournament.pending_registrations_count(), 2)

    def test_zero_without_pre_moderation(self):
        self._registration(is_approved=False)
        self.tournament.registrations_pre_moderation = False
        self.tournament.save()

        self.assertEqual(self.tournament.pending_registrations_count(), 0)

    def test_registered_players_count_excludes_pending(self):
        self.tournament.opened_registration = True
        self.tournament.save()
        self._registration(is_approved=True)
        self._registration(is_approved=False)
        url = self.tournament.get_url().replace("/de/", "/en/", 1)

        self.assertIn("Registered players 1", self.client.get(url).content.decode())

    def test_alert_shown_only_with_pre_moderation(self):
        self._registration(is_approved=False)
        url = self.tournament.get_url().replace("/de/", "/en/", 1)

        self.assertIn("Registrations waiting for approval: 1", self.client.get(url).content.decode())

        self.tournament.registrations_pre_moderation = False
        self.tournament.save()
        self.assertNotIn("Registrations waiting for approval", self.client.get(url).content.decode())


class CountryDropdownTest(TestCase):
    def setUp(self):
        self.country = Country.objects.create(code="AT", name="Austria")
        Country.objects.create(code="DE", name="Germany")
        self.tournament = Tournament.objects.create(
            name="Country Cup",
            slug="country-cup",
            end_date=datetime.date(2026, 1, 1),
            country=self.country,
            is_upcoming=True,
            opened_registration=True,
        )

    def _form(self, data=None, initial=None):
        form_initial = {"tournament": self.tournament}
        form_initial.update(initial or {})
        return TournamentRegistrationForm(data=data, initial=form_initial)

    def test_choices_come_from_country_table(self):
        choices = self._form().fields["registration_country"].choices
        self.assertEqual(choices, [("", "---------"), ("Austria", "Austria"), ("Germany", "Germany")])

    def test_unknown_country_is_rejected(self):
        data = {
            "first_name": "Hans",
            "last_name": "Müller",
            "registration_country": "Ausitra",
            "city": "Wien",
            "email": "h@example.com",
            "allow_to_save_data": "on",
        }
        self.assertFalse(self._form(data=data).is_valid())

        data["registration_country"] = "Austria"
        self.assertTrue(self._form(data=data).is_valid(), self._form(data=data).errors)

    def test_participants_table_shows_country_not_city(self):
        TournamentRegistration.objects.create(
            tournament=self.tournament,
            first_name="Hans",
            last_name="Müller",
            city="Wien",
            registration_country="Austria",
            email="h@example.com",
            is_approved=True,
        )
        page = self.client.get(self.tournament.get_url().replace("/de/", "/en/", 1)).content.decode()

        self.assertIn("Austria", page)
        self.assertNotIn("Wien", page)


class WaitlistTest(TestCase):
    def setUp(self):
        country = Country.objects.create(code="AT", name="Austria")
        self.tournament = Tournament.objects.create(
            name="Graz Riichi Open",
            slug="graz-riichi-open",
            end_date=datetime.date(2026, 1, 1),
            country=country,
            is_upcoming=True,
        )

    def _registration(self, last_name="Müller", **kwargs):
        kwargs.setdefault("is_approved", False)
        return TournamentRegistration.objects.create(
            tournament=self.tournament,
            first_name="Hans",
            last_name=last_name,
            city="Wien",
            registration_country="Austria",
            email="h@example.com",
            **kwargs,
        )

    @staticmethod
    def _run(action, queryset):
        from unittest.mock import MagicMock

        action(MagicMock(), None, queryset)

    def test_numbers_increment_and_approved_rows_are_skipped(self):
        from tournament.admin import add_to_waitlist

        first = self._registration("First")
        second = self._registration("Second")
        approved = self._registration("Approved", is_approved=True)

        self._run(add_to_waitlist, TournamentRegistration.objects.all())

        first.refresh_from_db()
        second.refresh_from_db()
        approved.refresh_from_db()
        self.assertEqual(first.waitlist_number, 1)
        self.assertEqual(second.waitlist_number, 2)
        self.assertIsNone(approved.waitlist_number)

    def test_numbering_continues_after_a_removal(self):
        from tournament.admin import add_to_waitlist, remove_from_waitlist

        first = self._registration("First")
        self._registration("Second")
        self._run(add_to_waitlist, TournamentRegistration.objects.all())
        self._run(remove_from_waitlist, TournamentRegistration.objects.filter(pk=first.pk))

        first.refresh_from_db()
        self.assertIsNone(first.waitlist_number)

        # 1 is now free but not reused: numbering continues past the highest, leaving a gap
        later = self._registration("Later")
        self._run(add_to_waitlist, TournamentRegistration.objects.filter(pk=later.pk))
        later.refresh_from_db()
        self.assertEqual(later.waitlist_number, 3)

    def test_approving_clears_the_waitlist_number(self):
        registration = self._registration(waitlist_number=3)

        registration.is_approved = True
        registration.save()

        registration.refresh_from_db()
        self.assertIsNone(registration.waitlist_number)

    def test_table_renumbers_over_gaps(self):
        self._registration("Alpha", waitlist_number=3)
        self._registration("Beta", waitlist_number=7)
        self._registration("NotListed")

        page = self.client.get(self.tournament.get_url().replace("/de/", "/en/", 1)).content.decode()

        self.assertIn("Waiting list", page)
        waitlist_rows = page.split("Waiting list")[1]
        self.assertIn("Alpha", waitlist_rows)
        self.assertIn("Beta", waitlist_rows)
        self.assertNotIn("NotListed", waitlist_rows)
        # displayed 1, 2 — not the stored 3 and 7
        self.assertIn('<th scope="row">1</th>', waitlist_rows)
        self.assertIn('<th scope="row">2</th>', waitlist_rows)
        self.assertNotIn('<th scope="row">3</th>', waitlist_rows)

    def test_no_card_without_candidates(self):
        self._registration()
        page = self.client.get(self.tournament.get_url().replace("/de/", "/en/", 1)).content.decode()
        self.assertNotIn("Waiting list", page)
