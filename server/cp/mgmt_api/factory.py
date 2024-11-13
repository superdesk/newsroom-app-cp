#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Newsroom.
#
# Copyright 2021 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import os
import logging
import flask

from elasticsearch.exceptions import RequestError as ElasticRequestError
from werkzeug.exceptions import HTTPException
from superdesk.errors import SuperdeskApiError

from newsroom.factory import BaseNewsroomApp
from newsroom.auth_server.auth import JWTAuth


logger = logging.getLogger(__name__)

API_DIR = os.path.abspath(os.path.dirname(__file__))


class NewsroomMGMTAPI(BaseNewsroomApp):
    INSTANCE_CONFIG = "settings_mgmtapi.py"
    AUTH_SERVICE = JWTAuth

    def __init__(self, import_name=__package__, config=None, **kwargs):
        if not hasattr(self, "settings"):
            self.settings = flask.Config(".")

        if config and config.get("BEHAVE"):
            # ``superdesk.tests.update_config`` adds ``planning`` to ``INSTALLED_APPS``
            # So if we're running behave tests, reset this config here
            config["INSTALLED_APPS"] = []

        super(NewsroomMGMTAPI, self).__init__(
            import_name=import_name, config=config, **kwargs
        )

    def load_app_default_config(self):
        """
        Loads default app configuration
        """
        # default config from `content_api.app.settings`
        super().load_app_default_config()
        # default config from `cp.mgmt_api.default_settings`
        self.config.from_object("cp.mgmt_api.default_settings")

    def load_app_instance_config(self):
        """
        Loads instance configuration defined on the newsroom-app repo level
        """
        # config from newsroom-app settings_newsapi.py file
        super().load_app_instance_config()
        # config from env var
        self.config.from_envvar("MGMT_API_SETTINGS", silent=True)

    def run(self, host=None, port=None, debug=None, **options):
        if not self.config.get("MGMT_API_ENABLED", False):
            raise RuntimeError("Management API is not enabled")

        super(NewsroomMGMTAPI, self).run(host, port, debug, **options)

    def setup_error_handlers(self):
        def json_error(err):
            return flask.jsonify(err), err["code"]

        def handle_werkzeug_errors(err):
            return json_error(
                {
                    "error": str(err),
                    "message": getattr(err, "description") or None,
                    "code": getattr(err, "code") or 500,
                }
            )

        def superdesk_api_error(err):
            return json_error(
                {
                    "error": err.message or "",
                    "message": err.payload,
                    "code": err.status_code or 500,
                }
            )

        def assertion_error(err):
            return json_error(
                {
                    "error": err.args[0] if err.args else 1,
                    "message": str(err),
                    "code": 400,
                }
            )

        def base_exception_error(err):
            if (
                type(err) is ElasticRequestError
                and err.error == "search_phase_execution_exception"
            ):
                return json_error(
                    {"error": 1, "message": "Invalid search query", "code": 400}
                )

            return json_error(
                {
                    "error": err.args[0] if err.args else 1,
                    "message": str(err),
                    "code": 500,
                }
            )

        for cls in HTTPException.__subclasses__():
            self.register_error_handler(cls, handle_werkzeug_errors)

        self.register_error_handler(SuperdeskApiError, superdesk_api_error)
        self.register_error_handler(AssertionError, assertion_error)
        self.register_error_handler(Exception, base_exception_error)


def get_app(config=None, **kwargs):
    return NewsroomMGMTAPI(__name__, config=config, **kwargs)
