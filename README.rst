..
    This file is part of INSPIRE.
    Copyright (C) 2014-2017 CERN.

    INSPIRE is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    INSPIRE is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.

    In applying this license, CERN does not waive the privileges and immunities
    granted to it by virtue of its status as an Intergovernmental Organization
    or submit itself to any jurisdiction.


==============
 INSPIRE-Next
==============


About
=====

INSPIRE is the leading information platform for High Energy Physics (HEP) literature.
It provides users with high quality, curated metadata covering the entire corpus of
HEP and the fulltext of all such articles that are Open Access.

This repository contains the source code of the next version of INSPIRE, which is
currently under development, but already available at `<https://labs.inspirehep.net>`_.
It is based on version 3 of the `Invenio Digital Library Framework`_.

A preliminary version of the documentation is available on `Read the Docs`_.


.. _`Invenio Digital Library Framework`: http://inveniosoftware.org/
.. _`Read the Docs`: https://inspirehep.readthedocs.io/en/latest/



Running tests
=============

1. docker compose -f docker-compose.test.yml up
2. On the `worker`  container run `scripts/clear_pycache`
3. On the `worker`  container run `pytest ...`
