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


class KnwKBData(DataSet):

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


class KnwKBRVALData(DataSet):

    class KnwKBRVALData_1:
        id = 29575
        m_key = u'b'
        m_value = u'Accelerators'
        id_knwKB = 8

    class KnwKBRVALData_2:
        id = 29576
        m_key = u'a'
        m_value = u'Astrophysics'
        id_knwKB = 8

    class KnwKBRVALData_3:
        id = 29577
        m_key = u'c'
        m_value = u'Computing'
        id_knwKB = 8

    class KnwKBRVALData_4:
        id = 29578
        m_key = u'e'
        m_value = u'Experiment-HEP'
        id_knwKB = 8

    class KnwKBRVALData_5:
        id = 29579
        m_key = u'x'
        m_value = u'Experiment-Nucl'
        id_knwKB = 8

    class KnwKBRVALData_6:
        id = 29580
        m_key = u'q'
        m_value = u'General Physics'
        id_knwKB = 8

    class KnwKBRVALData_7:
        id = 29581
        m_key = u'g'
        m_value = u'Gravitation and Cosmology'
        id_knwKB = 8

    class KnwKBRVALData_8:
        id = 29582
        m_key = u'i'
        m_value = u'Instrumentation'
        id_knwKB = 8

    class KnwKBRVALData_9:
        id = 29583
        m_key = u'l'
        m_value = u'Lattice'
        id_knwKB = 8

    class KnwKBRVALData_10:
        id = 29584
        m_key = u'm'
        m_value = u'Math and Math Physics'
        id_knwKB = 8

    class KnwKBRVALData_11:
        id = 29585
        m_key = u'o'
        m_value = u'Other'
        id_knwKB = 8

    class KnwKBRVALData_12:
        id = 29586
        m_key = u'p'
        m_value = u'Phenomenology-HEP'
        id_knwKB = 8

    class KnwKBRVALData_13:
        id = 29587
        m_key = u't'
        m_value = u'Theory-HEP'
        id_knwKB = 8

    class KnwKBRVALData_14:
        id = 29588
        m_key = u'n'
        m_value = u'Theory-Nucl'
        id_knwKB = 8


class KnwKBDDEFData(DataSet):

    class KnwKBDDEFData_1:
        id_knwKB = 7
        id_collection = 2
        output_tag = u'110__u'
        search_expression = u'371__a:"*%*"'

__all__ = ('KnwKBData', 'KnwKBRVALData', 'KnwKBDDEFData')
