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

"""Celery tasks provided by Record module."""

from __future__ import absolute_import, division, print_function

from celery import current_app, shared_task
from celery.utils.log import get_task_logger
from elasticsearch.helpers import scan

from invenio_search import current_search_client as es
from invenio_db import db
from invenio_records.api import Record

from inspire_schemas import api
from inspirehep.modules.search.utils import dotter

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def replace_old_ref_for_record(old_record_ref, new_record_ref):
    ignore_refs_in_fields = current_app.conf.get('IGNORE_REFS_IN_FIELDS')
    schemas_names = current_app.conf.get('INSPIRE_JSON_SCHEMAS')
    possible_fields = get_ref_fields(ignore_refs_in_fields, schemas_names)
    old_control_number = get_recid_from_url(old_record_ref)

    record_uuids = es_search_pointing_ids_from_ref_in_terms(possible_fields, old_control_number)

    with db.session.begin_nested():
        for rec_uuid in record_uuids:
            rec_db = Record.get_record(rec_uuid)
            find_and_replace_old_link_with_new_link_in_record(rec_db, new_record_ref, old_record_ref)
            rec_db.commit()
    db.session.commit()


def get_recid_from_url(url):
    try:
        res = int(url.split('/')[-1])
    except ValueError:
        res = None
    return res


def find_ref_fields_in_schema(schema_name):
    def construct_str(string):
        result_list = []
        for splited_path in string.split('.'):
            if '_records' in splited_path:
                result_list.append(splited_path[:-len('_records')] + '_recid')
                break
            elif '_record' in splited_path:
                result_list.append(splited_path[:-len('_record')] + '_recid')
                break
            elif 'records' in splited_path:
                result_list.append(splited_path[:-len('records')] + 'recid')
                break
            elif 'record' in splited_path:
                result_list.append(splited_path[:-len('record')] + 'recid')
                break

            result_list.append(splited_path)
        return '.'.join(result_list)[1:]

    schema = api.load_schema(schema_name)
    all_fields_dotted = dotter(schema.get('properties'), '', [])
    fields = []
    for field_dotted in all_fields_dotted:
        if 'record' in field_dotted:
            contructed_field = construct_str(field_dotted)
            fields.append(contructed_field)

    return fields


def get_ref_fields(ignore_refs_in_fields, schemas_names):
    if schemas_names is None:
        schemas_names = ['hep', 'authors', 'conferences',
                         'experiments', 'institutions',
                         'jobs', 'journals']
    fields_to_check_links = []

    for schema_name in schemas_names:
        fields_to_check_links += find_ref_fields_in_schema(schema_name)

    set_fields_to_check_links = set(fields_to_check_links)
    set_bad_fields = set(ignore_refs_in_fields)

    return list(set_fields_to_check_links - set_bad_fields)


def es_search_pointing_ids_from_ref_in_terms(fields_recid, old_control_number):
    body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            _key: {"value": old_control_number}}
                    }
                    for _key in fields_recid]
            }
        },
        "fields": [
            "_id"
        ]
    }

    scroll = scan(es, query=body, index="records-*")

    for response in scroll:
        rec_uuid = response['_id']

        yield rec_uuid


def find_and_replace_old_link_with_new_link_in_record(record, new_link, old_link):
    bad_fields = ['deleted_recid', 'new_recid']

    if isinstance(record, dict):
        for key, value in record.items():
            if key not in bad_fields:
                if isinstance(value, dict):
                    for key_ref in value:
                        if key_ref == '$ref':
                            if old_link == value.get('$ref'):
                                value['$ref'] = new_link

            find_and_replace_old_link_with_new_link_in_record(value, new_link, old_link)
    elif isinstance(record, list):
        for item in record:
            find_and_replace_old_link_with_new_link_in_record(item, new_link, old_link)
