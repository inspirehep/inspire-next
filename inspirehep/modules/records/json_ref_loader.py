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

"""Resource-aware json reference loaders to be used with jsonref."""

from __future__ import absolute_import, division, print_function

import re

from flask import current_app, url_for
from jsonref import JsonLoader, JsonRef
from werkzeug.urls import url_parse

import jsonresolver
from jsonresolver.contrib.jsonref import json_loader_factory

from inspire_schemas.utils import load_schema
from inspirehep.modules.pidstore.utils import get_pid_type_from_endpoint
from inspirehep.utils import record_getter


class AbstractRecordLoader(JsonLoader):
    """Base for resource-aware record loaders.

    Resolves the refered resource by the given uri by first checking against
    local resources.
    """

    def get_record(self, pid_type, recid):
        raise NotImplementedError()

    def get_remote_json(self, uri, **kwargs):
        parsed_uri = url_parse(uri)
        # Add http:// protocol so uri.netloc is correctly parsed.
        server_name = current_app.config.get('SERVER_NAME')
        if not re.match('^https?://', server_name):
            server_name = 'http://{}'.format(server_name)
        parsed_server = url_parse(server_name)

        if parsed_uri.netloc and parsed_uri.netloc != parsed_server.netloc:
            return super(AbstractRecordLoader, self).get_remote_json(uri,
                                                                     **kwargs)
        path_parts = parsed_uri.path.strip('/').split('/')
        if len(path_parts) < 2:
            current_app.logger.error('Bad JSONref URI: {0}'.format(uri))
            return None

        endpoint = path_parts[-2]
        pid_type = get_pid_type_from_endpoint(endpoint)
        recid = path_parts[-1]
        res = self.get_record(pid_type, recid)
        return res


class ESJsonLoader(AbstractRecordLoader):
    """Resolve resources by retrieving them from Elasticsearch."""

    def get_record(self, pid_type, recid):
        try:
            return record_getter.get_es_record(pid_type, recid)
        except record_getter.RecordGetterError:
            return None


class DatabaseJsonLoader(AbstractRecordLoader):

    def get_record(self, pid_type, recid):
        try:
            return record_getter.get_db_record(pid_type, recid)
        except record_getter.RecordGetterError:
            return None


es_record_loader = ESJsonLoader()
db_record_loader = DatabaseJsonLoader()
SCHEMA_LOADER_CLS = json_loader_factory(
    jsonresolver.JSONResolver(
        plugins=['invenio_jsonschemas.jsonresolver']
    )
)
"""Used in invenio-jsonschemas to resolve relative $ref."""


def load_resolved_schema(name):
    """Load a JSON schema with all references resolved.

    Args:
        name(str): name of the schema to load.

    Returns:
        dict: the JSON schema with resolved references.

    Examples:
        >>> resolved_schema = load_resolved_schema('authors')

    """
    schema = load_schema(name)
    return JsonRef.replace_refs(
        schema,
        base_uri=url_for('invenio_jsonschemas.get_schema', schema_path='records/{}.json'.format(name)),
        loader=SCHEMA_LOADER_CLS()
    )


def replace_refs(obj, source='db'):
    """Replaces record refs in obj by bypassing HTTP requests.

    Any reference URI that comes from the same server and references a resource
    will be resolved directly either from the database or from Elasticsearch.

    :param obj:
        Dict-like object for which '$ref' fields are recursively replaced.
    :param source:
        List of sources from which to resolve the references. It can be any of:
            * 'db' - resolve from Database
            * 'es' - resolve from Elasticsearch
            * 'http' - force using HTTP

    :returns:
        The same obj structure with the '$ref' fields replaced with the object
        available at the given URI.
    """
    loaders = {
        'db': db_record_loader,
        'es': es_record_loader,
        'http': None
    }
    if source not in loaders:
        raise ValueError('source must be one of {}'.format(loaders.keys()))

    loader = loaders[source]
    return JsonRef.replace_refs(obj, loader=loader, load_on_repr=False)
