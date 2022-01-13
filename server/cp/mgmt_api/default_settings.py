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

from superdesk.default_settings import urlparse
from newsroom.web.default_settings import ( # noqa
    env,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_SETTINGS,
    CONTENTAPI_ELASTICSEARCH_URL,
    CONTENTAPI_ELASTICSEARCH_SETTINGS,
)

MGMTAPI_URL = env('MGMTAPI_URL', 'http://localhost:5500/api')
server_url = urlparse(MGMTAPI_URL)
URL_PREFIX = env("MGMTAPI_URL_PREFIX", server_url.path.strip("/")) or ""

BLUEPRINTS = []

CORE_APPS = [
    'cp.mgmt_api.companies',
    'cp.mgmt_api.users',
    'cp.mgmt_api.products',
    'cp.mgmt_api.topics',
]

INSTALLED_APPS = []

# newsroom default db and index names
MONGO_DBNAME = env('MONGO_DBNAME', 'newsroom')
# mongo
MONGO_URI = env('MONGO_URI', f'mongodb://localhost/{MONGO_DBNAME}')
CONTENTAPI_MONGO_URI = env('CONTENTAPI_MONGO_URI', f'mongodb://localhost/{MONGO_DBNAME}')
# elastic
ELASTICSEARCH_INDEX = env('ELASTICSEARCH_INDEX', MONGO_DBNAME)
CONTENTAPI_ELASTICSEARCH_INDEX = env('CONTENTAPI_ELASTICSEARCH_INDEX', MONGO_DBNAME)

FILTER_AGGREGATIONS = False
ELASTIC_DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

MGMT_API_AUTH_TYPE = env('MGMT_API_AUTH_TYPE', 'cp.mgmt_api.auth.auth')
AUTH_SERVER_SHARED_SECRET = env("AUTH_SERVER_SHARED_SECRET", "")
