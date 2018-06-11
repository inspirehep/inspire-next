# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage migrator from INSPIRE legacy instance."""

from __future__ import absolute_import, division, print_function

import csv
import os
import sys
import traceback
import warnings

from itertools import dropwhile
from textwrap import dedent

import click
import jsonschema

from dojson.contrib.marc21.utils import create_record

from flask import current_app
from flask.cli import with_appcontext

from inspire_dojson import marcxml2record
from inspire_schemas.api import validate

from inspirehep.utils.schema import ensure_valid_schema
from .models import LegacyRecordsMirror
from .tasks import (
    add_citation_counts,
    migrate_from_file,
    migrate_from_mirror,
    migrate_record_from_legacy,
    populate_mirror_from_file,
)
from .utils import get_collection


def halt_if_debug_mode(force):
    message = '''\
    The application is running in debug mode, which leaks memory when doing
    many database operations. To avoid problems, disable debug mode. This can
    be done by setting "DEBUG=False" in the config or setting the environment
    variable "APP_DEBUG=False". If you know what you are doing, you can pass
    the "--force" flag to disable this check.
    '''
    if not force and current_app.config.get('DEBUG'):
        click.echo(dedent(message), err=True)
        sys.exit(1)


@click.group()
def migrate():
    """Commands to migrate records from legacy."""


@migrate.command('file')
@click.argument('file_name', type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.option('--mirror-only', '-m', is_flag=True, default=False,
              help='Only mirror the records without instead of doing a full migration.')
@click.option('--wait', '-w', is_flag=True, default=False,
              help='Wait for migration to complete. This only has an effect if the -w flag is not set.')
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force the task to run even in debug mode.')
@with_appcontext
def migrate_file(file_name,
                 mirror_only=False,
                 wait=False,
                 force=False):
    """Migrate the records in the provided file.

    The file can be an (optionally-gzipped) XML file containing MARCXML, or a
    prodsync tarball.
    """
    halt_if_debug_mode(force=force)
    click.echo("Migrating records from file: {0}".format(file_name))

    populate_mirror_from_file(file_name)
    if not mirror_only:
        migrate_from_mirror(wait_for_results=wait)


@migrate.command()
@click.option('--all', '-a', 'also_migrate', flag_value='all',
              help='Migrate all records, irrespective of their status.')
@click.option('--broken', '-b', 'also_migrate', flag_value='broken',
              help='Also migrate broken records, which did not migrate correctly in the previous run.')
@click.option('--wait', '-w', is_flag=True, default=False,
              help='Wait for migration to complete. This only has an effect if the -w flag is not set.')
@click.option('-f', '--force', is_flag=True, default=False,
              help='Force the task to run even in debug mode.')
@with_appcontext
def mirror(also_migrate=None,
           wait=False,
           force=False):
    """Migrate records from the mirror.

    By default, only records that have not been migrated yet are migrated.
    """
    halt_if_debug_mode(force=force)
    migrate_from_mirror(also_migrate=also_migrate, wait_for_results=wait)


@migrate.command()
@click.argument('recid', type=int)
@with_appcontext
def record(recid):
    """Migrate a single record from legacy."""
    click.echo('Migrating record {recid} from INSPIRE legacy'.format(recid=recid))
    migrate_record_from_legacy(recid)


@click.group()
def migrator():
    """DEPRECATED Command related to migrating INSPIRE data."""
    warnings.warn('The "migrator" command is deprecated, use "migrate" instead.', DeprecationWarning)


@migrator.command()
@click.option('--file-input', '-f',
              help='Specific collections to migrate.')
@click.option('--remigrate-broken', '-b', is_flag=True,
              default=False, help='Try to remigrate broken records')
@click.option('--remigrate-all', '-a', is_flag=True,
              default=False, help='Remigrate all records')
@click.option('--wait', '-w', type=bool, default=False,
              help='Wait for migrator to complete.')
def populate(file_input=None,
             remigrate_broken=False,
             remigrate_all=False,
             wait=False):
    """DEPRECATED Populates the system with records from migrator files.

    Usage: inveniomanage migrator populate -f prodsync20151117173222.xml.gz
    """
    warnings.warn('The "migrator" command is deprecated, use "migrate" instead.', DeprecationWarning)
    if remigrate_broken:
        click.echo("Remigrate broken records...")
        migrate_from_mirror.delay(only_broken=True)
    elif remigrate_all:
        click.echo("Remigrate all records...")
        migrate_from_mirror.delay(only_broken=False)
    elif file_input and not os.path.isfile(file_input):
        click.echo("{0} is not a file!".format(file_input), err=True)
    elif file_input:
        click.echo("Migrating records from file: {0}".format(file_input))

        migrate_from_file(os.path.abspath(file_input), wait_for_results=wait)


@migrator.command()
@click.option('--recid', '-r', type=int, help="recid on INSPIRE")
def one(recid):
    """DEPRECATED Migrate one record from legacy."""
    warnings.warn('The "migrator" command is deprecated, use "migrate" instead.', DeprecationWarning)
    click.echo('Migrating record {recid} from INSPIRE legacy'.format(recid=recid))
    migrate_record_from_legacy(recid)


@migrator.command()
def count_citations():
    """Adds field citation_count to every record in 'HEP' and calculates its proper value."""
    click.echo("Adding citation_count to all records")
    add_citation_counts()


@migrator.command()
@click.option('--output', '-o', default="/tmp/broken-records.csv",
              help='Specifiy where to report errors.')
@with_appcontext
def reporterrors(output):
    """Reports in a friendly way all failed records and corresponding motivation."""
    click.echo("Reporting broken records into {0}".format(output))
    errors = {}
    results = LegacyRecordsMirror.query.filter(LegacyRecordsMirror.valid == False) # noqa: ignore=F712
    results_length = results.count()
    with click.progressbar(results.yield_per(100), length=results_length) as bar:
        for obj in bar:
            marc_record = create_record(obj.marcxml, keep_singletons=False)
            collection = get_collection(marc_record)
            if 'DELETED' in collection:
                continue
            recid = int(marc_record['001'])
            try:
                json_record = marcxml2record(obj.marcxml)
            except Exception as err:
                tb = u''.join(traceback.format_tb(sys.exc_info()[2]))
                errors.setdefault((collection, 'dojson', tb), []).append(recid)
                continue

            ensure_valid_schema(json_record)

            try:
                validate(json_record)
            except jsonschema.exceptions.ValidationError as err:
                exc = [
                    row
                    for row in str(err).splitlines()
                    if row.startswith('Failed validating')
                ][0]
                details = u'\n'.join(
                    dropwhile(
                        lambda x: not x.startswith('On instance'),
                        str(err).splitlines()
                    )
                )
                errors.setdefault(
                    (collection, 'validation', exc), []
                ).append((recid, details))
                continue

    with open(output, "w") as out:
        csv_writer = csv.writer(out)
        for (collection, stage, error), elements in errors.iteritems():
            if stage == 'dojson':
                csv_writer.writerow((
                    collection,
                    stage,
                    error,
                    '\n'.join(
                        'http://inspirehep.net/record/{}'.format(recid)
                        for recid in elements
                    )
                ))
            else:
                for recid, details in elements:
                    csv_writer.writerow((
                        collection,
                        stage,
                        error,
                        'http://inspirehep.net/record/{}'.format(recid),
                        details
                    ))
    click.echo("Dumped errors into {}".format(output))
