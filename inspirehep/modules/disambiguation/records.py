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

"""Set of methods to create and update records."""

from __future__ import absolute_import, division, print_function

from celery.utils.log import get_task_logger
from flask import current_app, url_for

from invenio_db import db

from invenio_records.signals import after_record_insert

from inspirehep.dojson import utils as inspire_dojson_utils
from inspirehep.modules.pidstore.minters import inspire_recid_minter
from inspirehep.modules.records.api import InspireRecord
from inspirehep.modules.disambiguation.receivers import (
    append_new_record_to_queue,
)

logger = get_task_logger(__name__)


def _get_author_schema():
    """Generate schema URL to be inserted in $schema field."""
    # FIXME: Use a dedicated method when #1355 will be resolved.
    return url_for(
        "invenio_jsonschemas.get_schema",
        schema_path=current_app.config.get(
            'DISAMBIGUATION_AUTHORS_SCHEMA_PATH'
        )
    )


def create_author(profile):
    """Create a new author profile based on a given signature.

    The method receives a dictionary representing an author.
    Based on the values, it creates a dictionary in the invenio_records format.
    After all the fields are processed, the method calls create_record
    from invenio_records.api to put the new record.

    :param profile:
        A signature representing an author's to be created as a profile.

        Example:
            profile = {u'affiliations': [{u'value': u'Yerevan Phys. Inst.'}],
                       u'alternative_name': None,
                       u'curated_relation': False,
                       u'email': None,
                       u'full_name': u'Chatrchyan, Serguei',
                       u'inspire_id': None,
                       u'orcid': None,
                       u'profile': u'',
                       u'recid': None,
                       u'role': None,
                       u'uuid': u'd63537a8-1df4-4436-b5ed-224da5b5028c'}

    :return:
        A recid, where the new profile can be accessed.

        Example:
            "1234"
    """
    name = profile.get('full_name')

    # Template of an initial record.
    record = {
        '$schema': _get_author_schema(),
        '_collections': ['Authors'],
        'name': {'value': name},
    }

    # The author's email address.
    # Unfortunately the method will not correlate a given e-mail address
    # with an affiliation.
    if 'email' in profile:
        email = profile.get('email')

        record['positions'] = []
        record['positions'].append({'email': email})

    # The author can be a member of more than one affiliation.
    if 'affiliations' in profile:
        affiliations = profile.get('affiliations')

        if 'positions' not in record:
            record['positions'] = []

        for affiliation in affiliations:
            name = affiliation.get('value')
            recid = affiliation.get('recid', None)

            if recid:
                record['positions'].append(
                    {'institution': {'name': name, 'recid': recid}})
            else:
                record['positions'].append(
                    {'institution': {'name': name}})

    # FIXME: The method should also collect the useful data
    #        from the publication, like category field, subject,
    #        etc.

    # Disconnect the signal on insert of a new record.
    after_record_insert.disconnect(append_new_record_to_queue)

    # Create a new author profile.
    record = InspireRecord.create(record, id_=None)

    # Create Inspire recid.
    record_pid = inspire_recid_minter(record.id, record)

    # Extend the new record with Inspire recid and self key.
    record['control_number'] = record_pid.pid_value
    record['self'] = inspire_dojson_utils.get_record_ref(
        record_pid.pid_value, 'authors')

    # Apply the changes.
    record.commit()
    db.session.commit()

    # Reconnect the disconnected signal.
    after_record_insert.connect(append_new_record_to_queue)

    # Report.
    logger.info("Created profile: %s", record_pid.pid_value)

    # Return the recid of new profile to which signatures will point to.
    return record_pid.pid_value
