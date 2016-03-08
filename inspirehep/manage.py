# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Manage INSPIRE instance."""

from __future__ import print_function

import json

import sys

from time import sleep

import click

from flask import current_app
from flask_script import prompt_choices

from inspirehep.ext.cache_manager import cache_manager

from invenio_base.globals import cfg

from invenio_ext.es import es
from invenio_ext.script import Manager



manager = Manager(usage=__doc__)


@manager.command
def reindexhp():
    """Reindex all Holding Pen objects."""
    from invenio_workflows.models import BibWorkflowObject
    from inspirehep.modules.migrator.tasks import reindex_holdingpen_object

    query = BibWorkflowObject.query.with_entities(BibWorkflowObject.id).filter(
        BibWorkflowObject.id_parent == None).all()  # noqa

    click.echo(
        click.style(
            'Going to reindex {0} records (holdingpen)...'.format(len(query)), fg='green'
        )
    )
    click.echo()

    with click.progressbar(query) as holdingpen_ids:
        for obj_id in holdingpen_ids:
            reindex_holdingpen_object(obj_id[0])

    click.echo()
    click.echo(click.style('DONE', fg='green'))


@manager.option('--collection', '-c', dest='collections',
                action='append',
                default=[],
                help='Specific collection to reindex.')
@manager.option('--query', '-q', dest='query',
                action='store',
                default="",
                help='Specific query to use.')
@manager.option('--bulksize', '-b', dest='bulk_size',
                action='store',
                default=500,
                help='Bulk size.')
def reindex(collections=[], query="", bulk_size=500):
    """Reindex all records from metadata store."""
    from invenio_search.api import Query
    from invenio_records.models import RecordMetadata
    from invenio_records.api import get_record
    from inspirehep.modules.migrator.tasks import reindex_recids

    if not collections:
        collections = ["HEP"]

    prefix_query = ""
    if query:
        prefix_query += "{0} AND ".format(query)

    for coll in collections:
        final_query = '{0}collection:"{1}"'.format(prefix_query, coll)

        recids = []
        for recid_tuple in RecordMetadata.query.with_entities(RecordMetadata.id).all():
            recid = recid_tuple[0]
            if Query(final_query).match(get_record(recid)):
                recids.append(recid)

        click.echo(
            click.style(
                'Going to reindex {0} records from {1}...'.format(len(recids), coll), fg='yellow'
            )
        )
    reindex_recids.delay(list(recids), int(bulk_size))
    click.echo()


@manager.option('--rebuild', '-r', dest='rebuild',
                action='store_true',
                default=False,
                help='Whether to rebuild indexes rather than just create them empty.')
@manager.option('--holdingpen', '-h', dest='holdingpen',
                action='store_true',
                default=False,
                help='Whether to reindex also the holdingpen indexes.')
@manager.option('--delete-old', '-d', dest='delete_old',
                action='store_true',
                default=False,
                help='Delete old index after the rebuild process has completed.')
@manager.option('--index-name', '-n', dest='index_names',
                action='append',
                default=[],
                help='Specific name of an index to recreate/rebuild.')
def create_indices(rebuild=False, holdingpen=False, delete_old=False, index_names=[]):
    """Create or recreate the indices for records and holdingpen."""
    from invenio_search.registry import mappings

    if rebuild:
        plugins = [plugin['name'] for plugin in es.nodes.info()['nodes'].values()[0]['plugins']]
        if 'reindexing' not in plugins:
            print("ERROR: Please install the ElasticSearch reindexing plugin if you want to rebuild indexes.", file=sys.stderr)
            sys.exit(1)

    if index_names:
        indices = index_names
    else:
        indices = set(current_app.config["SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING"].values())
        indices.add(current_app.config['SEARCH_ELASTIC_DEFAULT_INDEX'])
    for index in indices:
        possible_indices = [index]
        if holdingpen:
            possible_indices.append(current_app.config['WORKFLOWS_HOLDING_PEN_ES_PREFIX'] + index)
        click.echo(click.style('Rebuilding {0}... '.format(index), fg='yellow'), nl=False)
        mapping = {}
        mapping_filename = index + ".json"
        if mapping_filename in mappings:
            mapping = json.load(open(mappings[mapping_filename], "r"))
        recreate_index(index, mapping, rebuild=rebuild)
        click.echo(click.style('OK', fg='green'))
        if holdingpen:
            # Create Holding Pen index
            if mapping:
                mapping['mappings']['record']['properties'].update(
                    current_app.config['WORKFLOWS_HOLDING_PEN_ES_PROPERTIES']
                )
            name = current_app.config['WORKFLOWS_HOLDING_PEN_ES_PREFIX'] + index
            click.echo(click.style(
                'Rebuilding {0}... '.format(name), fg='yellow'
            ), nl=False)
            recreate_index(name, mapping, rebuild=rebuild)
            click.echo(click.style('OK', fg='green'))


@manager.command
def delete_indices():
    """Delete all the indices for records and holdingpen."""
    from invenio.base.globals import cfg

    indices = set(cfg["SEARCH_ELASTIC_COLLECTION_INDEX_MAPPING"].values())
    indices.add(cfg['SEARCH_ELASTIC_DEFAULT_INDEX'])
    holdingpen_indices = [
        cfg['WORKFLOWS_HOLDING_PEN_ES_PREFIX'] + name for name in list(indices)
    ]
    indices.update(holdingpen_indices)
    click.echo(click.style('Deleting ALL indices...', fg='red'), nl=False)
    with click.progressbar(indices) as indices_to_delete:
        for index in indices_to_delete:
            es.indices.delete(index=index, ignore=404)
    click.echo()
    click.echo(click.style('DONE', fg='green'))


def recreate_index(name, mapping, rebuild=False, delete_old=True):
    """Recreate an ElasticSearch index."""
    if rebuild:
        from copy import deepcopy
        original_es_hosts = deepcopy(es.transport.hosts)
        try:
            # The reindexing plugin can work only with one client.
            es.transport.hosts = es.transport.hosts[:1]
            es.transport.set_connections(es.transport.hosts)
            current_index = es.indices.get_alias(name).keys()[0]
            future_index = name + '_v2' if current_index.endswith('_v1') else name + '_v1'
            original_number_of_documents = es.count(current_index)['count']
            es.indices.delete(index=future_index, ignore=404)
            es.indices.create(index=future_index, body=mapping)
            es.indices.put_settings(index=current_index, body={'index': {'blocks': {'read_only': True}}})
            es.indices.put_settings(index=future_index, body={'index': {'refresh_interval': -1}})
            try:
                code, answer = es.cat.transport.perform_request('POST', '/{}/_reindex/{}/'.format(current_index, future_index))
                assert code == 200
                assert answer['acknowledged']
                reindex_name = answer['name']
                while reindex_name in es.cat.transport.perform_request('GET', '/_reindex/')[1]['names']:
                    # Let's poll to wait for finishing
                    sleep(3)
                es.indices.flush(future_index, wait_if_ongoing=True)
                if original_number_of_documents != es.count(future_index)['count']:
                    click.echo("ERROR when reindexing {current_index} into {future_index}. Bailing out.".format(
                        current_index=current_index,
                        future_index=future_index))
                    return False
            finally:
                es.indices.put_settings(index=current_index, body={'index': {'blocks': {'read_only': False}}})
                es.indices.put_settings(index=future_index, body={'index': {'refresh_interval': "1s"}})
                es.indices.forcemerge(index=future_index, max_num_segments=5)

            es.indices.put_alias(index=future_index, name=name)
            if delete_old:
                es.indices.delete(index=current_index)
        finally:
            # We restore all the correct connections
            es.transport.hosts = original_es_hosts
            es.transport.set_connections(es.transport.hosts)
    else:
        es.indices.delete(index=name + "_v1", ignore=404)
        es.indices.delete(index=name + "_v2", ignore=404)
        es.indices.create(index=name + "_v1", body=mapping)
        es.indices.put_alias(index=name + "_v1", name=name)
    return True


@manager.option('-c', '--cache', dest='cache_name',
                default=None,
                help='Name of the cached view type to invalidate.')
def invalidate_cache(cache_name):
    """Invalidate cache of certain type e.g. brief, citation etc."""
    possible_caches = cfg['CACHED_VIEWS'].keys() + ['all']
    how_many_invalidated = 0

    if cache_name not in possible_caches:
        cache_name = prompt_choices(name="Choose cache view you want to invalidate: ", choices=possible_caches)
    if cache_name == 'all':
        click.echo('Removing all cached views...')
        how_many_invalidated = cache_manager.invalidate_all_cached_views()
        click.echo('Invalidated {count} cached views.'.format(count=how_many_invalidated))
    elif cache_name in possible_caches:
        click.echo('Removing {cache_type} view...'.format(cache_type=cache_name))
        how_many_invalidated = cache_manager.invalidate_all_certain_views(cache_name)
        click.echo('Invalidated {count} cached views.'.format(count=how_many_invalidated))
    else:
        click.echo('Chosen cached view does not exist.')
