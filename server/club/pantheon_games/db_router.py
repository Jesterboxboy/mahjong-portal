# -*- coding: utf-8 -*-

class PantheonRouter(object):
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "pantheon_games":
            return "pantheon"
        return "default"

    def db_for_write(self, model, **hints):
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return "default"
