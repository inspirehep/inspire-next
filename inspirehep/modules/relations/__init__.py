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

"""Relations."""

from flask import current_app

from werkzeug.urls import url_parse
from invenio_db import db
from invenio_records.signals import after_record_insert, after_record_update

from .models import Relations


def uri_to_uuid(uri):
    parsed_uri = url_parse(uri)

    path_parts = parsed_uri.path.strip('/').split('/')
    if len(path_parts) < 2:
        current_app.logger.error('Bad JSONref URI: {0}'.format(uri))
        return None

    record_type = path_parts[-2]
    recid = path_parts[-1]
    return PersistentIdentifier.get(record_type, recid).id, record_type


def crawl_json_for_ref(json, root='', relation=''):
    ret = []
    if hasattr(json, 'iteritems'):
        for key, value in json.iteritems():
            if key == '$ref':
                ret.append((root, value))
            elif hasattr(value, 'iteritems'):
                ret.extend(crawl_json_for_ref(
                    value,
                    '{0}.{1}'.format(root, key),
                    '{0}.{1}'.format(root, key)
                ))
            elif isinstance(value, list):
                for i, elem in enumerate(value):
                    ret.extend(crawl_json_for_ref(
                        value,
                        '{0}.{1}[{2}]'.format(root, key, i),
                        '{0}.{1}'.format(root, key),
                    ))
    return ret


@after_record_insert.connect
@after_record_update.connect
def upsert_relation(json):
    with db.session.begin_nested():
        from_id, from_type = uri_to_uuid(json['$self'])
        Relations.query().filter(Relations.id_from == id_from).delete()
        for ref, path, relation in crawl_json_for_ref(json):
            to_id, to_type = uri_to_uuid(ref)
            Relations.create(
                from_id=from_id,
                from_type=from_type,
                to_id=to_id,
                to_type=to_type,
                relation=relation,
                path=path
            )
