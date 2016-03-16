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
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Resource-aware json reference loaders to be used with jsonref."""

from jsonref import JsonLoader, JsonRef
from werkzeug.urls import url_parse

from flask import current_app

from inspirehep.utils import record_getter


class AbstractRecordLoader(JsonLoader):
    """Base for resource-aware record loaders.

    Resolves the refered resource by the given uri by first checking against
    local resources.
    """

    def get_record(self, record_type, recid):
        raise NotImplementedError()

    def get_remote_json(self, uri, **kwargs):
        parsed_uri = url_parse(uri)
        # Normalize optional 'http://' protocol in the config.
        server_name = current_app.config.get('SERVER_NAME')
        if not server_name.startswith('http://'):
            server_name = 'http://{}'.format(server_name)
        parsed_server = url_parse(server_name)

        if parsed_uri.netloc and parsed_uri.netloc != parsed_server.netloc:
            return super(AbstractRecordLoader, self).get_remote_json(uri,
                                                                     **kwargs)
        path_parts = parsed_uri.path.strip('/').split('/')
        if len(path_parts) < 2:
            current_app.logger.error('Bad JSONref URI: {0}'.format(uri))
            return None

        record_type = path_parts[-2]
        recid = path_parts[-1]
        res = self.get_record(record_type, recid)
        return res


class ESJsonLoader(AbstractRecordLoader):
    """Resolve resources by retrieving them from Elasticsearch."""

    def get_record(self, record_type, recid):
        try:
            return record_getter.get_es_record(record_type, recid)
        except record_getter.RecordGetterError:
            return None


class DatabaseJsonLoader(AbstractRecordLoader):

    def get_record(self, record_type, recid):
        try:
            return record_getter.get_db_record(record_type, recid)
        except record_getter.RecordGetterError:
            return None


es_record_loader = ESJsonLoader()
db_record_loader = DatabaseJsonLoader()


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
    return JsonRef.replace_refs(obj, loader=loader)
