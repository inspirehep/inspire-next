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

from .proxies import current_graph_db as graph_db

from invenio_records.models import RecordMetadata


@click.group()
def relations():
    """Command related to relations in INSPIRE"""
    logging.basicConfig()


@relations.command()
@with_appcontext
def drop_db():
    """Remove everything from graph db."""
    # TODO: implement it
    return NotImplementedError()


@relations.command()
@with_appcontext
def migrate_graph():
    """Create graph representation of data from relational db
    and migrate to to graph db.
    """
    from .migrate import migrate
    records, count = get_all_records_in_db()

    migrate(records, count, current_app.config['RELATIONS_STORAGEDIR'])


@relations.command()
@with_appcontext
def generate_csvs():
    """Generates CSV files and CYPHER scripts based on the relational db.
    """
    from .migrate import generate_csv_and_cypher_scripts
    records, count = get_all_records_in_db()

    generate_csv_and_cypher_scripts(records,
                                    count,
                                    current_app.config['RELATIONS_STORAGEDIR'])


@with_appcontext
def get_all_records_in_db():
    """Retrieve all records from relational db."""
    return (
        RecordMetadata().query.yield_per(1000),
        RecordMetadata().query.count()
        )
