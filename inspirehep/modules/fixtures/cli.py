# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Manage fixtures for INSPIRE site."""

from __future__ import print_function

import click

from flask_cli import with_appcontext

from .files import init_all_storage_paths
from .users import init_users_and_permissions


@click.group()
def fixtures():
    """Command related to migrating INSPIRE data."""


@fixtures.command()
@with_appcontext
def init():
    """Init the system with fixtures."""
    init_all_storage_paths()
    init_users_and_permissions()
