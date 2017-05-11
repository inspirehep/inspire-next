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


Overview of Inspire-next
========================

This diagram is a very high level overview of Inspire-next project.

|

.. image:: images/overview_diagram.png
    :height: 300
    :width: 660

|

- Incoming sources (records) to Inspire-next.
    * Legacy: the old website of Inspire.
    * Submission Forms: records provided by catalogers and users.
    * Crawler: collects records from other sources (websites/repositories).

- Workflows: Process part of Inspire-next.

- Data: there are two storing points of Inspire-next:
    * DataBase (PostgreSQL)
    * Search Engine (ElasticSearch)
