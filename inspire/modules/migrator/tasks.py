# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage migration from INSPIRE legacy instance."""

from __future__ import absolute_import

from invenio_ext.sqlalchemy import db
from invenio_records.api import Record as record_api
from invenio_records.models import Record

from inspire.dojson.hep import hep
from inspire.dojson.institutions import institutions
from inspire.dojson.journals import journals
from inspire.dojson.experiments import experiments
from inspire.dojson.hepnames import hepnames
from inspire.dojson.jobs import jobs
from inspire.dojson.conferences import conferences
from inspire.dojson.processors import _collection_in_record

from dojson.contrib.marc21.utils import create_record as marc_create_record

from lxml import etree

from invenio_celery import celery


@celery.task
def migrate(source, **kwargs):
    """Main migration function."""
    from dojson.contrib.marc21.utils import split_stream
    with db.session.begin_nested():
        for record in split_stream(open(source)):
            create_record(etree.tostring(record, method='html'), force=True)
    db.session.commit()


def create_record(data, force=False):
    record = marc_create_record(data)
    if _collection_in_record(record, 'institution'):
        json = institutions.do(record)
    elif _collection_in_record(record, 'experiment'):
        json = experiments.do(record)
    elif _collection_in_record(record, 'journals'):
        json = journals.do(record)
    elif _collection_in_record(record, 'hepnames'):
        json = hepnames.do(record)
    elif _collection_in_record(record, 'job') or \
            _collection_in_record(record, 'jobhidden'):
        json = jobs.do(record)
    elif _collection_in_record(record, 'conferences'):
        json = conferences.do(record)
    else:
        json = hep.do(record)

    if force and any(key in json for key in ('control_number', 'recid')):
        try:
            control_number = json['control_number']
        except KeyError:
            control_number = json['recid']
        control_number = int(control_number)
        # Searches if record already exists.
        record = Record.query.filter_by(id=control_number).first()
        if record is None:
            # Adds the record to the db session.
            rec = Record(id=control_number)
            db.session.add(rec)
        record_api.create(json)
