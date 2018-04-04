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

"""
IMPORTANT This script is a copy/paste of:
https://github.com/inspirehep/inspire-next/issues/2629

It is unreliable and absolutely unmaintainable.
It will be refactored with this user story:
https://its.cern.ch/jira/browse/INSPIR-249

To be run with:
$ /usr/bin/time -v inspirehep hal push
"""

from __future__ import absolute_import, division, print_function

import datetime
import time

import click

from flask import current_app

from invenio_records.models import RecordMetadata
from inspirehep.modules.hal.core.tei import convert_to_tei
from inspirehep.modules.hal.core.sword import create, update


def _set_config():
    # Set the proper configuration.
    current_app.config['HAL_COL_IRI'] = 'https://api.archives-ouvertes.fr/sword/hal'
    current_app.config['HAL_EDIT_IRI'] = 'https://api.archives-ouvertes.fr/sword/'


def run():
    click.echo('>> PUSH TO HAL\n')
    username = raw_input('Username: ')
    password = raw_input('Password: ')
    limit = raw_input('Limit the query? [number, 0 means no limit] ')
    limit = int(limit)
    yield_amt = raw_input('Yield amount? [suggested 100] ')
    yield_amt = int(yield_amt)
    if yield_amt < 10:
        raise Exception('Yield amount should be >= 10')
    click.echo('\n')

    start = time.time()
    _set_config()
    current_app.config['HAL_USER_NAME'] = username
    current_app.config['HAL_USER_PASS'] = password
    records = RecordMetadata.query.filter(RecordMetadata.json['_export_to'].op('@>')('{"HAL": true}'))
    if limit > 0:
        records = records.limit(limit)
    # log_file = os.path.join(os.path.dirname(__file__), 'HAL.log')
    log_file = '/opt/inspire/HAL.log'
    ok = ko = 0
    with open(log_file, 'w') as f:
        for i, raw_record in enumerate(records.yield_per(yield_amt)):
            if i % 10 == 0:
                now = str(datetime.timedelta(seconds=time.time() - start))
                click.echo('%s records processed in %s: %s ok, %s ko' % (i, now, ok, ko))
            record = raw_record.json
            if 'Literature' in record['_collections'] or 'HAL Hidden' in record['_collections']:
                try:
                    tei = convert_to_tei(record)
                except Exception as e:
                    f.write('EXC TEI: %s %s\n' % (record['control_number'], str(e)))
                    # ko.append(record['control_number'])
                    ko += 1
                    continue

                success = False
                for _ in range(2):
                    try:
                        hal_id = ''
                        ids = record.get('external_system_identifiers', [])
                        for id_ in ids:
                            if id_['schema'] == 'HAL':
                                hal_id = id_['value']
                        if hal_id:
                            update(tei.encode('utf8'), hal_id.encode('utf8'))
                            f.write('UPD: %s %s\n' % (record['control_number'], hal_id))
                        else:
                            receipt = create(tei.encode('utf8'))
                            f.write('NEW: %s %s\n' % (record['control_number'], receipt.id))
                        success = True
                        break
                    except Exception as e:
                        continue
                if success:
                    # ok.append(record['control_number'])
                    ok += 1
                else:
                    f.write('EXC HAL: %s %s\n' % (record['control_number'], str(e)))
                    # ko.append(record['control_number'])
                    ko += 1
    click.echo('%s records processed in %s: %s ok, %s ko' % (i, now, ok, ko))
