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

from invenio_records.signals import before_record_insert, before_record_update

@before_record_insert.connect
def catch_citations_insert(sender, *args, **kwargs):
    a = []
    if 'references' in sender:
        references = sender['references']
        for reference in references:
            recid = reference.get('recid')
            if recid is not None:
                a.append(recid)


@before_record_update.connect
def catch_citations_update(sender, *args, **kwargs):
    a = []
    if 'references' in sender:
        references = sender['references']
        for reference in references:
            recid = reference.get('recid')
            if recid is not None:
                a.append(recid)
    b = []
    if 'control_number' in sender:
        from invenio_ext.es import es
        recid = sender['control_number']
        rec = es.get(index='hep', id=recid)
        rec = rec['_source']
        if 'references' in rec:
            references = rec['references']
            for reference in references:
                recid = reference.get('recid')
                if recid is not None:
                    b.append(recid)
    f = filter(lambda x: x not in b, a) + filter(lambda x: x not in a, b)
