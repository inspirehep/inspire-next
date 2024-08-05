#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
#
# inspirehep is free software; you can redistribute it and/or modify it under
# the terms of the MIT License; see LICENSE file for more details.


# Verify that all services are running before continuing
check_ready() {
    RETRIES=10
    echo "Checking service $1"
    while ! $2
    do
        echo "Waiting for $1, $((RETRIES--)) remaining attempts..."
        sleep 5
        if [ $RETRIES -eq 0 ]
        then
            echo "Couldn't reach $1"
            exit 1
        fi
    done
}
_db_check(){ docker compose -f docker-compose.test.yml exec --user postgres test-database bash -c "pg_isready" &>/dev/null; }
check_ready "postgres" _db_check

_es_check(){ curl -sL -w "%{http_code}\\n" "http://localhost:9200/" -o /dev/null | grep '200' &> /dev/null; }
check_ready "Elasticsearch" _es_check

_redis_check(){ docker compose -f docker-compose.test.yml exec test-redis bash -c 'redis-cli ping' | grep 'PONG' &> /dev/null; }
check_ready "redis" _redis_check
