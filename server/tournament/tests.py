# -*- coding: utf-8 -*-

import datetime
from unittest.mock import patch

from django.test import TestCase, override_settings

from account.models import User
from settings.models import Country
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
