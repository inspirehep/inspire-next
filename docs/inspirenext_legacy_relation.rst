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


2.6.1 Relation between Inspire-next and Legacy
----------------------------------------------

Inspire-next is the next generation of Inspire. The previous version of Inspire called Legacy.

`Legacy
<http://inspirehep.net/>`_ website.

`Inspire-next
<https://qa.inspirehep.net/>`_ website (under construction).

In the bellow diagram is presented the current relation between them.

.. image:: images/inspirenext_legacy_relation.png
    :height: 250
    :width: 660

- Inspire-next/Labs has incoming records flow from:
    * Literature Suggest: records provided by catalogers and users.
    * HEP Crawl: Crawler that collects records from other sources (websites/repositories).
    * Legacy: Old records can be inserted to Inspire-next database via migration.

- Legacy database has the existing records and new records coming from Inspire-next.

- Migration is the procedure that converts and stores records in both sides (Inspire-next and Legacy).
    * Records from Legacy are in MarcXML format and in Inspire-next are in JSON format. So,
      transformation rules are provided in order to translate MarcXML to JSON and vice versa.
      Those rules are provided by DoJson module.
