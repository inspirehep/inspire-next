..
    This file is part of INSPIRE.
    Copyright (C) 2017 CERN.

    INSPIRE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    INSPIRE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.

    In applying this licence, CERN does not waive the privileges and immunities
    granted to it by virtue of its status as an Intergovernmental Organization
    or submit itself to any jurisdiction.


2.3.1 Inspire Record Class
--------------------------

The Inpire record is derived by the base class of Invenio record. Inspire record is used mainly for the
back-end processes and for the outer world is used the inherited classes of Inspire record. According to
the bellow diagram, Inspire record is the base class and ES record (ElasticSearch) is the derived class.
The data that are given to the front-end are inherited classes from ES record:

    * AuthorsRecord
    * LiteratureRecord
    * JobsRecord
    * ConferencesRecord
    * InstitutionsRecord
    * ExperimentsRecord
    * JournalsRecord

|

.. image:: images/inspire_record.png
    :height: 300
    :width: 660

|

TIP: the above classes are written in the following files.
    * ``inspirehep/modules/records/wrappers.py``
    * ``inspirehep/modules/records/api.py``
