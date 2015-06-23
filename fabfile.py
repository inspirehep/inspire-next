# -*- coding: utf-8 -*-

"""Utility tasks for INSPIRE Labs."""

from fabric.api import *


@task
def clean_assets():
    """Helper to ensure all assets are up to date."""
    local("rm -rf $VIRTUAL_ENV/var/invenio.base-instance/static/")
    local("rm -rf inspire/base/static/gen/")
    local("rm -rf inspire/base/static/vendors/")
    local("inveniomanage bower -i bower-base.json > bower.json")
    local("bower install")
    local("inveniomanage collect")
