# -*- coding: utf-8 -*-
#
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
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

from datetime import datetime
from fixture import DataSet


class OaiHARVESTData(DataSet):

    class OaiHARVEST_1:
        from invenio.modules.oaiharvester.models import get_default_arguments
        id = 1
        name = "arXivb"
        baseurl = "http://export.arxiv.org/oai2"
        metadataprefix = "arXiv"
        lastrun = datetime.now()
        workflows = "generic_harvesting_workflow_with_bibsched"
        setspecs = ["hep-lat"]
        arguments = get_default_arguments()


class OaiREPOSITORYData(DataSet):

    class OaiREPOSITORY_2:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=CERN;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 2
        setSpec = u'CERN'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'CERN'
        setCollection = u'CERN'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_3:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=HEP;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 3
        setSpec = u'INSPIRE:HEP'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'INSPIRE HEP publications'
        setCollection = u'HEP'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_4:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=Institutions;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 4
        setSpec = u'INSPIRE:Institutions'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'INSPIRE Institutions'
        setCollection = u'Institutions'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_5:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=Conferences;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 5
        setSpec = u'INSPIRE:Conferences'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'Conferences'
        setCollection = u'Conferences'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_6:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=Conferences;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 6
        setSpec = u'CERN:arXiv'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'CERN arXiv records'
        setCollection = u'CERN'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_7:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=Jobs;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 7
        setSpec = u'INSPIRE:Jobs'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'INSPIRE Jobs'
        setCollection = u'Jobs'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_8:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=Experiments;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 8
        setSpec = u'INSPIRE:Experiments'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'INSPIRE Experiments'
        setCollection = u'Experiments'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_8:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=Journals;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 8
        setSpec = u'INSPIRE:Journals'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'INSPIRE Journals'
        setCollection = u'Journals'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''

    class OaiREPOSITORY_8:
        f1 = u''
        f2 = u''
        f3 = u''
        setRecList = None
        setDefinition = u'c=HepNames;p1=;f1=;m1=;op1=a;p2=;f2=;m2=;op2=a;p3=;f3=;m3=;'
        last_updated = datetime.now()
        id = 8
        setSpec = u'INSPIRE:HepNames'
        setDescription = u''
        p3 = u''
        p1 = u''
        setName = u'INSPIRE HepNames'
        setCollection = u'HepNames'
        p2 = u''
        m1 = u''
        m3 = u''
        m2 = u''
