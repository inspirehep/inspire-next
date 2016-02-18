# -*- coding: utf-8 -*-

"""Utility tasks for INSPIRE Labs."""

from fabric.api import *
from fabric.context_managers import lcd


@task
def clean_assets():
    """Helper to ensure all assets are up to date."""
    local("rm -rf $VIRTUAL_ENV/var/inspirehep-instance/static")
    local("inspirehep npm")
    with lcd('$VIRTUAL_ENV/var/inspirehep-instance/static'):
        local("npm install")
        local("inspirehep collect -v")
        local("inspirehep assets build")
