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

"""Communication handler with Beard Celery service."""

from __future__ import (
    absolute_import,
    division,
    print_function,
)

import celery
from flask import current_app


def make_beard_clusters(records, signatures):
    """Dispatch a clustering task to Beard Celery instance.

    The method receives a list of records and a list of signatures representing
    records that will be clustered by Beard algorithm.

    The argument 'records' is a list of dictionaries containing values like
    authors of a particular record, earliest date recorded of the publication
    and finally publication UUID.

    The argument 'signatures' represents the phonetic block,
    that is being currently computed by one of 'disambiguation' workers.

    In order to check what is being used in order to cluster signatures,
    check 'create_beard_record' and 'create_beard_signatures' methods in
    'search.py' as the reference.

    The method dispatches a Celery task to Beard server.
    Beard algorithm distinguishes different authors for
    *the same* signature block. The clustered authors are then returned
    in the format of dictionaries.

    :param records:
        A list of the records, where at least one author will be
        clustered (by having the same phonetic block).

        Example:
            records = [{'authors': [u'Hohm, Olaf', u'Wang, Yi-Nan'],
                       'publication_id': u'13c3cca8-b0bf-42f5-90d4-...',
                       'year': u'2015'}]

    :param signatures:
        A list of signatures belonging to the same signature block,
        which is currently being clustered.

        Example:
            signatures =  [{'author_affiliation': u'MIT, Cambridge, CTP',
                            'author_name': u'Wang, Yi-Nan',
                            'publication_id': u'13c3cca8-b0bf-42f5-90d4-...',
                            'signature_id': u'a4156520-4248-a57f-949c361e0dd0',
                            'author_recid': u'10123',
                            'author_claimed': False}]

    :return:
        A tuple containing clusters matched with existing author profiles and
        clusters for which new profile must be created.

        The first 'bucket' is a list of dictionaries, where each key
        represents recid of an existing author profile. The second 'bucket'
        is a list of dictionaries as well, however with enumerated keys,
        which are meaningless.

        Except clustering, Beard Celery instance is also responsible for
        matching output of a clustering job with a current state of Inspire
        system, ie. current links between signatures and their author profiles.
        The matching process is done using simplex algorithm for maximising
        overlap between new clusters (Beard output) with signatures clustered
        by belonging to the same profile.

        To see what is the workflow behind Beard Celery instance, check
        https://github.com/inspirehep/beard-server

        Example:
            [{u'10123': [u'a4156520-4248-a57f-949c361e0dd0']}, {}]
    """
    if records and signatures:
        clusters = celery.current_app.send_task(
            'beard_server.tasks.make_clusters',
            (records, signatures),
            queue=current_app.config.get('DISAMBIGUATION_QUEUE'))

        return clusters
