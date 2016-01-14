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

from invenio_celery import celery

from .signals import after_citation_count_update


@celery.task
def update_citation_count_for_records(recids):
    """Updates field citation_count for the records with given recids."""
    for recid in recids:
        update_citation_count.delay(recid)


@celery.task
def update_citation_count(recid):
    """Updates field citation_count for the record with given recid."""

    from invenio_ext.es import es
    from .utils import calculate_citation_count
    from elasticsearch import TransportError

    doc_update = {'citation_count': None}
    calculate_citation_count(recid, doc_update)

    try:
        es.update(index='hep', id=recid, doc_type='record', body={'doc': doc_update})
    except TransportError:
        pass
    after_citation_count_update.send(recid)
