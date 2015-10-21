# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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


"""Tasks for citations management."""

from __future__ import print_function

from flask import current_app

from inspire.modules.citations.models import Citation, Citation_Log

from invenio_base.globals import cfg

from invenio.celery import celery

from invenio_records.api import get_record

import requests


def update_records_citations(new_citations):
    """Gets a set of records that need to be updated
    and querys database to get all citations for each record.
    Saves this ciattions on a new set and updates the record.
    """
    citees = set()
    for id in new_citations:
        cit = Citation.query.filter_by(citer=id).all()
        for rec in cit:
            citees.add(rec.citee)
        rec = get_record(id)
        if rec is not None:
            rec.update({"references_id": list(citees)})
        else:
            current_app.logger.exception(
                "citations: record with id:%d not found", id)
        citees.clear()


@celery.task()
def update_citations_log():
    """Fetches all unfetched log entries from the legacy site.
    The first time it runs fetches everything and then everytime it runs
    fetches all new entries (by looking the id of the last entry and
    quering legacy site based on this value).

    The corresponding population of the citations database takes places on
    Citation_Log.save() method inside the models.py file.
    """
    # Getting the id of the last log entry
    last_entry = Citation_Log.query.order_by(Citation_Log.id.desc()).first()
    # Incase the database is empty it starts fetching all the data
    if last_entry is None:
        last_entry = 0
    # If it's not empty if fetches every entry with an id greater than
    # last_entry
    else:
        last_entry = last_entry.id
    url_ap = cfg.get("CITATIONS_FETCH_LEGACY_URL") + "?id=" + str(last_entry)
    data = requests.get(url_ap).json()
    # Set that keep track of papers that need to be updated (re-fetch
    # citations)
    new_citations = set()
    while data:
        for entry in data:
            id = entry[0]
            citee = entry[1]
            citer = entry[2]
            citation_type = entry[3]
            action_date = entry[4]
            last_entry = id
            cit = Citation_Log(id, citee, citer, action_date, citation_type)
            cit.save()
            new_citations.add(citer)
        url_ap = cfg.get("CITATIONS_FETCH_LEGACY_URL") + \
            "?id=" + str(last_entry)
        data = requests.get(url_ap).json()
    update_records_citations(new_citations)
