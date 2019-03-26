#!/bin/bash

set -e
#cd /opt/ops_platform

#git stash
#git pull origin python3:python3
#
#pip3 install -r requirements.txt


if [ -n "$DB_HOST" ]; then
    sed -i "s@{{\s*DB_HOST\s*}}@$DB_HOST@g" AI/settings.py.template
fi

if [ -n "$DB_NAME" ]; then
    sed -i "s@{{\s*DB_NAME\s*}}@$DB_NAME@g" AI/settings.py.template
fi

if [ -n "$DB_USER" ]; then
    sed -i "s@{{\s*DB_USER\s*}}@$DB_USER@g" AI/settings.py.template
fi

if [ -n "$DB_PASSWORD" ]; then
    sed -i "s@{{\s*DB_PASSWORD\s*}}@$DB_PASSWORD@g" AI/settings.py.template
fi

if [ -n "$DB_PORT" ]; then
    sed -i "s@{{\s*DB_PORT\s*}}@$DB_PORT@g" AI/settings.py.template
fi

if [ -n "$REDIS_HOST" ]; then
    sed -i "s@{{\s*REDIS_HOST\s*}}@$REDIS_HOST@g" AI/settings.py.template
fi

if [ -n "$REDIS_PSW" ]; then
    sed -i "s@{{\s*REDIS_PSW\s*}}@$REDIS_PSW@g" AI/settings.py.template
fi

if [ -n "$AIP_ID" ]; then
    sed -i "s@{{\s*AIP_ID\s*}}@$AIP_ID@g" AI/settings.py.template
fi

if [ -n "$AIP_KEY" ]; then
    sed -i "s@{{\s*AIP_KEY\s*}}@$AIP_KEY@g" AI/settings.py.template
fi

if [ -n "$AIP_SECRET_KEY" ]; then
    sed -i "s@{{\s*AIP_SECRET_KEY\s*}}@$AIP_SECRET_KEY@g" AI/settings.py.template
fi

if [ -n "$CASSANDRE_USER" ]; then
    sed -i "s@{{\s*CASSANDRE_USER\s*}}@$CASSANDRE_USER@g" AI/settings.py.template
fi

if [ -n "$CASSANDRE_PASSWORD" ]; then
    sed -i "s@{{\s*CASSANDRE_PASSWORD\s*}}@$CASSANDRE_PASSWORD@g" AI/settings.py.template
fi

if [ -n "$CASSANDRE_IP" ]; then
    sed -i "s@{{\s*CASSANDRE_IP\s*}}@$CASSANDRE_IP@g" AI/settings.py.template
fi

if [ -n "$CASSANDRE_PORT" ]; then
    sed -i "s@{{\s*CASSANDRE_PORT\s*}}@$CASSANDRE_PORT@g" AI/settings.py.template
fi

if [ -n "$CASSANDRE_KEYSPACE" ]; then
    sed -i "s@{{\s*CASSANDRE_KEYSPACE\s*}}@$CASSANDRE_KEYSPACE@g" AI/settings.py.template
fi


mv AI/settings.py.template AI/settings.py

exec "$@"
