# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


from __future__ import absolute_import, division, print_function


import click
from flask import current_app
from flask_cli import with_appcontext
import logging

from inspirehep.modules.relations.command_producers import delete_all
from inspirehep.modules.relations.migrate import (
    generate_csvs_and_commands,
    generate_loader,
    migrate,
    run_cypher_commands,
    run_loading_script
)

from inspirehep.modules.relations.utils import get_all_records_in_db


@click.group()
def relations():
    """Command related to relations in INSPIRE"""
    logging.basicConfig()


@relations.command()
@with_appcontext
def drop_db():
    """Remove everything from graph db."""
    run_cypher_commands(
        [delete_all()]
    )


@relations.command()
@with_appcontext
def migrate_graph():
    """Create graph representation of data from relational db
    and migrate to to graph db.
    """
    records, count = get_all_records_in_db()

    migrate(records, count, current_app.config['RELATIONS_STORAGEDIR'])


@relations.command()
@with_appcontext
def generate_csvs():
    """Generate CSV files and CYPHER scripts based on the relational db.
    """
    records, count = get_all_records_in_db()

    commands = generate_csvs_and_commands(
        records, count, current_app.config['RELATIONS_STORAGEDIR'])
    generate_loader(current_app.config['RELATIONS_STORAGEDIR'], commands)


@relations.command()
@with_appcontext
def load_csvs():
    """Run cypher loader given that it exists.
    """
    run_loading_script(current_app.config['RELATIONS_STORAGEDIR'])
