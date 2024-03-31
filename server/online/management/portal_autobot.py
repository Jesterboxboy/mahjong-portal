# -*- coding: utf-8 -*-

import logging

from django.utils.translation import activate

from online.handler import TournamentHandler
from online.models import TournamentNotification
from tournament.models import Tournament

logger = logging.getLogger("tournament_bot")

# todo: move into self
tournament_handler = TournamentHandler()


class PortalAutoBot:
    def init(self, tournamentId, lobbyId):
        tournament = Tournament.objects.get(id=tournamentId)
        # todo for tenhou.net gameType
        tournament_handler.init(tournament, lobbyId, None, TournamentHandler.TELEGRAM_DESTINATION)

    @staticmethod
    def open_registration(chatId):
        logger.info("Open confirmation stage")
        logger.info(f"Chat ID {chatId}")
        tournament_handler.open_registration()

    @staticmethod
    def close_registration(chatId):
        logger.info("Close registration")
        logger.info(f"Chat ID {chatId}")
        tournament_handler.close_registration()

    @staticmethod
    def check_new_notifications(tournamentId):
        notification = TournamentNotification.objects.filter(
            is_processed=False, destination=TournamentNotification.TELEGRAM, failed=False, tournament_id=tournamentId
        ).last()

        if not notification:
            return None

        try:
            logger.info(f"Notification id={notification.id} found")
            message = tournament_handler.get_notification_text("ru", notification)
            return {"message": message, "notification_id": notification.id}
        except Exception as e:
            notification.failed = True
            notification.save()
            logger.error(e, exc_info=e)

    @staticmethod
    def process_notification(notificationId, tournamentId):
        notification = TournamentNotification.objects.get(
            id=notificationId, tournament_id=tournamentId, is_processed=False
        )

        if not notification:
            return None

        try:
            notification.is_processed = True
            notification.failed = False
            notification.save()
            logger.info(f"Notification id={notification.id} update to processed")
        except Exception as e:
            notification.failed = True
            notification.save()
            logger.error(e, exc_info=e)

    @staticmethod
    def prepare_next_round():
        logger.info("Prepare next round")

        return tournament_handler.prepare_next_round(reshuffleInPortal=False)

    @staticmethod
    def confirm_player(nickname, telegram_username):
        activate("ru")

        return tournament_handler.confirm_participation_in_tournament(nickname, telegram_username=telegram_username)

    @staticmethod
    def admin_confirm_player(friend_id, nickname, telegram_username):
        activate("ru")

        return tournament_handler.confirm_participation_in_tournament(
            nickname, telegram_username=telegram_username, friend_id=friend_id, is_admin=True
        )

    @staticmethod
    def create_start_game_notification(tour, table_number, notification_type, missed_players):
        tournament_handler.create_start_game_notification(
            int(tour), int(table_number), int(notification_type), missed_players
        )

    @staticmethod
    def game_finish(log_id, players, log_content, log_time):
        activate("ru")

        return tournament_handler.game_finish(log_id, players, log_content, log_time)

    @staticmethod
    def get_tournament_status():
        logger.info("Get tournament status command")
        activate("ru")
        return tournament_handler.get_tournament_status()

    @staticmethod
    def get_allowed_players():
        return tournament_handler.get_allowed_players()

    @staticmethod
    def add_game_log(log_link):
        activate("ru")

        return tournament_handler.add_game_log(log_link)
