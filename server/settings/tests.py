# -*- coding: utf-8 -*-

from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase, override_settings

from settings.admin import FreyConnectorForm
from settings.models import FreyConnector


@override_settings(PANTHEON_ADMIN_ID="5", PANTHEON_ADMIN_COOKIE="env-token")
class FreyConnectorTest(TestCase):
    def test_env_fallback_then_db_wins(self):
        self.assertEqual(FreyConnector.credentials(), ("5", "env-token"))
        FreyConnector.objects.create(person_id=9, auth_token="db-token")
        self.assertEqual(FreyConnector.credentials(), (9, "db-token"))

    def test_password_fetches_token_and_is_not_stored(self):
        with patch("settings.admin.login_through_pantheon") as login:
            login.return_value = SimpleNamespace(person_id=42, auth_token="fresh")
            form = FreyConnectorForm(data={"email": " a@b.at ", "password": "pw"})
            self.assertTrue(form.is_valid(), form.errors)
            login.assert_called_once_with("a@b.at", "pw")
        connector = form.save()
        self.assertEqual((connector.person_id, connector.auth_token), (42, "fresh"))
        self.assertNotIn("pw", str(FreyConnector.objects.values().get()))

    def test_login_failure_is_a_form_error(self):
        with patch("settings.admin.login_through_pantheon", side_effect=Exception("Person not found")):
            form = FreyConnectorForm(data={"email": "a@b.at", "password": "pw"})
            self.assertFalse(form.is_valid())
            self.assertIn("Person not found", str(form.errors))
