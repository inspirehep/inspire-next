# -*- coding: utf-8 -*-
#
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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


class CollectionData(DataSet):

    class Hep:
        id = 1
        name = "HEP"
        dbquery = '980__a:"HEP"'
        names = {
            ('en', 'ln'): u'HEP',
        }

    class Institutions:
        id = 2
        name = 'Institutions'
        dbquery = '980__a:"INSTITUTION"'
        names = {
            ('en', 'ln'): u'Institutions',
        }

    class Jobs:
        id = 3
        name = 'Jobs'
        dbquery = '980__a:"JOB"'
        names = {
            ('en', 'ln'): u'Jobs',
        }

    class Conferences:
        id = 4
        name = 'Conferences'
        dbquery = '980__a:"CONFERENCES"'
        names = {
            ('en', 'ln'): u'Conferences',
        }

    class Hepnames:
        id = 5
        name = 'HepNames'
        dbquery = '980__a:"HEPNAMES"'
        names = {
            ('en', 'ln'): u'HepNames',
        }

    class Jobshidden:
        id = 6
        name = 'Jobs Hidden'
        dbquery = '980__a:"JOBHIDDEN"'
        names = {
            ('en', 'ln'): u'Jobs Hidden',
        }

    class Experiments:
        id = 7
        name = 'Experiments'
        dbquery = '980__a:"EXPERIMENT"'
        names = {
            ('en', 'ln'): u'Experiments',
        }

    class Journals:
        id = 8
        name = 'Journals'
        dbquery = '980__a:"JOURNALS"'
        names = {
            ('en', 'ln'): u'Journals',
        }

    class H1internalnotes:
        id = 10
        name = 'H1 Internal Notes'
        dbquery = '980__a:"H1-INTERNAL-NOTE"'
        names = {
            ('en', 'ln'): u'H1 Internal Notes',
        }

    class Hermesinternalnotes:
        id = 11
        name = 'HERMES Internal Notes'
        dbquery = '980__a:"HERMES-INTERNAL-NOTE"'
        names = {
            ('en', 'ln'): u'HERMES Internal Notes',
        }

    class Zeusinternalnotes:
        id = 12
        name = 'ZEUS Internal Notes'
        dbquery = '980__a:"ZEUS-INTERNAL-NOTE"'
        names = {
            ('en', 'ln'): u'ZEUS Internal Notes',
        }

    class D0internalnotes:
        id = 13
        name = 'D0 Internal Notes'
        dbquery = '980__a:"D0-INTERNAL-NOTE"'
        names = {
            ('en', 'ln'): u'D0 Internal Notes',
        }

    class Data:
        id = 14
        name = 'Data'
        dbquery = '980__a:"DATA"'
        names = {
            ('en', 'ln'): u'Data',
        }

    class Zeuspreliminarynotes:
        id = 15
        name = 'ZEUS Preliminary Notes'
        dbquery = '980__a:"ZEUS-PRELIMINARY-NOTE"'
        names = {
            ('en', 'ln'): u'ZEUS Preliminary Notes',
        }

    class H1preliminarynotes:
        id = 17
        name = 'H1 Preliminary Notes'
        dbquery = '980__a:"H1-PRELIMINARY-NOTE"'
        names = {
            ('en', 'ln'): u'H1 Preliminary Notes',
        }

    class D0preliminarynotes:
        id = 18
        name = 'D0 Preliminary Notes'
        dbquery = '980__a:"D0-PRELIMINARY-NOTE"'
        names = {
            ('en', 'ln'): u'D0 Preliminary Notes',
        }

    class Cern:
        id = 19
        name = 'CERN'
        dbquery = '980__a:"r:cern-* or aff:cern or cn:atlas or cn:cms or cn:lhcb or cn:alice or exp:cern* and 980__a:"HEP""'
        names = {
            ('en', 'ln'): u'CERN',
        }


class CollectiondetailedrecordpagetabsData(DataSet):

    class Collectiondetailedrecordpagetabs_1:
        tabs = u'metadata;references;citations;files;plots'
        id_collection = CollectionData.Hep.ref('id')

    class Collectiondetailedrecordpagetabs_2:
        tabs = u'metadata'
        id_collection = CollectionData.Hepnames.ref('id')

    class Collectiondetailedrecordpagetabs_3:
        tabs = u'metadata'
        id_collection = CollectionData.Jobs.ref('id')

    class Collectiondetailedrecordpagetabs_4:
        tabs = u'metadata'
        id_collection = CollectionData.Institutions.ref('id')

    class Collectiondetailedrecordpagetabs_5:
        tabs = u'metadata'
        id_collection = CollectionData.Experiments.ref('id')

    class Collectiondetailedrecordpagetabs_6:
        tabs = u'metadata'
        id_collection = CollectionData.Journals.ref('id')


class Collectionname(DataSet):

    class Collectionname_1:
        id_collection = 1
        ln = 'en'
        type = 'ln'
        value = 'HEP'

    class Collectionname_2:
        id_collection = 2
        ln = 'en'
        type = 'ln'
        value = 'Institutions'

    class Collectionname_3:
            id_collection = 3
            ln = 'en'
            type = 'ln'
            value = 'Jobs'

    class Collectionname_4:
            id_collection = 4
            ln = 'en'
            type = 'ln'
            value = 'Conferences'

    class Collectionname_5:
            id_collection = 5
            ln = 'en'
            type = 'ln'
            value = 'HepNames'

    class Collectionname_6:
            id_collection = 6
            ln = 'en'
            type = 'ln'
            value = 'Jobs Hidden'

    class Collectionname_7:
            id_collection = 7
            ln = 'en'
            type = 'ln'
            value = 'Experiments'

    class Collectionname_8:
            id_collection = 8
            ln = 'en'
            type = 'ln'
            value = 'Journals'

__all__ = ('CollectionData', 'CollectiondetailedrecordpagetabsData',
           'Collectionname')
