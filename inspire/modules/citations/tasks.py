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


"""Tasks for classifier."""

from __future__ import print_function

import json, urllib2,requests
import os, time

import cPickle as pickle

from functools import wraps

from invenio.celery import celery

from inspire.utils.helpers import (
    get_record_from_model,
)

from inspire.modules.citation.models import Citation, Citation_Log

def fetch_citations():
    url = "http://inspirehep.net/citations.py"
    url_ap = url
    last_entry  = 0
    data = requests.get(url_ap).json()
    #cit = Citation(1,2,"2015-09-07 12:18:54")
    #cit.save()
    #while(data):
    for entry in data:
        id = entry[0]
        citee = entry[1]
        citer = entry[2]
        citation_type = entry[3]
        action_date = entry[4]
        last_entry = id
        cit = Citation_Log(id,citee,citer,action_date,citation_type)
        cit.save
    cit.commit()


@celery.task()
def update():
    url = "http://inspirehep.net/citations.py"
    url_ap = url
    last_entry  = 0
    data = requests.get(url_ap).json()
    #while(data):
    #    for entry in data:
    #        id = entry[0]
    #        citee = entry[1]
    #        citer = entry[2]
    #        citation_type = entry[3]
    #        action_date = entry[4]
    #        last_entry = id
    #    print(data)
    #    time.sleep(1)
    #    url_ap = url + "?id=" + str(last_entry)
    #    data = requests.get(url_ap).json()
