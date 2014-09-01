# -*- coding: utf-8 -*-
#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

from fixture import DataSet
import pkg_resources
import os


class KnwKBData(DataSet):

    """ Definition of KBs available in INSPIRE."""

    class KnwKBData_1:
        id = 1
        name = u'WEBLINKS'
        description = u'Mapping of SPIRES abbreviations for URLs to ' +\
                      u'Displayable names'
        kbtype = u'w'

    class KnwKBData_2:
        id = 2
        name = u'JOURNALS'
        description = u'Mapping of journal abbreviations to full names'
        kbtype = u'w'

    class KnwKBData_3:
        id = 3
        name = u'COLLECTION'
        description = u'690C aliases'
        kbtype = u'w'

    class KnwKBData_4:
        id = 4
        name = u'SUBJECT'
        description = u'65017 aliases'
        kbtype = u'w'

    class KnwKBData_5:
        id = 5
        name = u'PDG'
        description = u'PDG codes'
        kbtype = u'w'

    class KnwKBData_6:
        id = 6
        name = u'CODENS'
        description = u'Coden to short title mappings'
        kbtype = u'w'

    class KnwKBData_7:
        id = 7
        name = u'InstitutionsCollection'
        description = u'A dynamic KB which searches all 371a and 110u ' + \
                      u'fields in the institutions collection, and ' + \
                      u'returns those records\' corresponding 110u fields.'
        kbtype = u'd'

    class KnwKBData_8:
        id = 8
        name = u'Subjects'
        description = u'Subjects KB (created for BibEdit)'
        kbtype = u'w'

    class KnwKBData_9:
        id = 9
        name = u'docextract-journals'
        description = u'Journals Abbreviations used by docextract'
        kbtype = u'w'

    class KnwKBData_10:
        id = 11
        name = u'ExperimentsCollection'
        description = u'A dynamic KB which searches all 119a fields in ' + \
                      u'the experiments collection, and returns those ' + \
                      u'records\' corresponding 119a fields.'
        kbtype = u'd'

    class KnwKBData_11:
        id = 15
        name = u'PACS'
        description = u'Contains translation of PACS to a readable form'
        kbtype = u'w'

    class KnwKBData_12:
        id = 18
        name = u'NOTE_COLLECTIONS'
        description = u'A list of 088 report-number prefixes for which ' + \
                      u'the 980-collection \'NOTE\' should be appended.'
        kbtype = u'w'

    class KnwKBData_13:
        id = 22
        name = u'HEPCOLLECTIONS'
        description = u'List of possible HEP Collections'
        kbtype = u'w'

    class KnwKBData_14:
        id = 23
        name = u'DEGREE'
        description = u'List of type of Degrees'
        kbtype = u'w'


class KnwKBDDEFData(DataSet):

    """Definition of dynamic KB parameters."""

    class KnwKBDDEFData_1:
        id_knwKB = 7
        id_collection = 2
        output_tag = u'110__u'
        search_expression = u'371__a:"*%*"'

    class KnwKBDDEFData_2:
        id_knwKB = 11
        id_collection = 7
        output_tag = u'119__a'
        search_expression = u'119__a:"*%*" | 119__u:"*%*" | 419__a:"*%*" | 245__a:"*%*"'


class KnwKBRVALData(DataSet):
    pass
    """ Install INSPIRE KBs """


def add_kb_values(kbfile, kb_id, idx):
    """Generate fixtures for KB values.

    Given a KB file and a KB id, this function will insert all.
    entries in the file into to the corresponding KB table in the database.
    """
    for line in kbfile:
        splitted_line = line.split('---')
        pair = []
        for part in splitted_line:
            if not part.strip():
                # We can ignore this one
                continue
            pair.append(part.strip())
        if len(pair) != 2:
            print "Error: %s" % (str(pair),)

        class obj:
            try:
                m_key = pair[0]
            except IndexError:
                print line
                print kb_id

            m_value = pair[1]
            id_knwKB = kb_id
        obj.__name__ = "kbval{0}".format(idx)
        setattr(KnwKBRVALData, obj.__name__, obj)
        idx += 1
    return idx


# Get all KB files available under knowledgeext/kb
kb_paths = [(file,
            pkg_resources.resource_filename('inspire.base.knowledgeext',
                                            'kb/' + file))
            for file in pkg_resources.resource_listdir('inspire.base.knowledgeext',
                                                       'kb')]

# Normalize the names of available KBs and create a dict:
# {lowercasename: kb_id}
kb_names = dict([(getattr(KnwKBData, x).name.lower(), getattr(KnwKBData, x).id)
                for x in dir(KnwKBData) if x.startswith("KnwKBData")])

idx = 0
for filename, path in kb_paths:
    kb_name = os.path.splitext(filename)[0]
    kb_id = None
    try:
        kb_id = kb_names[kb_name]
    except KeyError:
        pass
    if kb_id:
        with open(path, 'r') as f:
            idx = add_kb_values(f, kb_id, idx)

__all__ = ('KnwKBData', 'KnwKBDDEFData', 'KnwKBRVALData')
