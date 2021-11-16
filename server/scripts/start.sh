#!/bin/bash

set -x

cd /opt/newsroom/

# wait for elastic to be up
until $(curl --output /dev/null --silent --head --fail "${ELASTICSEARCH_URL}"); do
    sleep .5
done

until $(curl --output /dev/null --silent --fail "${WEBPACK_SERVER_URL}/manifest.json"); do
    sleep .5
done

# app init
python3 manage.py create_user admin@localhost.com admin admin admin true
python3 manage.py elastic_init

if [[ -d dump ]]; then
    mongorestore -h mongo --gzip dump
    python3 manage.py index_from_mongo --all
fi

exec "$@"
