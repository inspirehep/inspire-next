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

from inspirehep.utils.search import perform_es_search


def traverse(o, tree_types=(list, tuple)):
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value):
                yield subvalue
    else:
        yield o


def generate_booktitle(record):
    booktitle = ''
    pubinfo = ''
    if 'publication_info' in record:
        pubinfo = record['publication_info']
        for field in pubinfo:
            if 'reportnumber' in field:
                rn = field['reportnumber']
                if rn:
                    acronym = field['acronym']
                    if acronym:
                        booktitle = "%s: %s" % (rn, acronym, )
                    else:
                        records = perform_es_search(
                            "reportnumber:%s" % (rn,),
                            "records-hep"
                        )
                        if records:
                            rec = records.hits[0]
                            for title in rec['titles']:
                                booktitle = title.get('title', "")
                                if title.get('subtitle'):
                                    booktitle += ': ' + title.get('subtitle')
        if not booktitle:
            result = []
            for field in pubinfo:
                if 'pubinfo_freetext' in field:
                    result.append(field['pubinfo_freetext'])
            if result:
                if any(isinstance(i, list) for i in result):
                    nested_list = list(traverse(result))
                    booktitle = ', '.join(str(title) for title in nested_list)
                else:
                    booktitle = ', '.join(str(title) for title in result)
    return booktitle
