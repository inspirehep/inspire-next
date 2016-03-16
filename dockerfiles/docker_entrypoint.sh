#!/bin/bash

set -e

if [ ! -f /virtualenv/bin/activate ]; then
    virtualenv /virtualenv
    source /virtualenv/bin/activate
    pip install --upgrade pip-accel setuptools
else
    source /virtualenv/bin/activate
fi

find \( -name __pycache__ -o -name '*.pyc' \) -delete

exec "$@"
