..
    This file is part of INSPIRE.
    Copyright (C) 2015, 2016 CERN.

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


INSPIRE Tests
=======================

How to Run Selenium Tests
-------------------------


Via Docker
~~~~~~~~~~~~~~~~~

1. Setup the test environment in ``docker``. If you have not installed ``docker`` and ``docker-compose``, please install them (`Docker install guide`__)

.. _install_docker: https://github.com/inspirehep/inspire-next/pull/1015
__ install_docker_

2. Go in the root directory of inspire project and run the following command:

.. code-block:: bash

  docker-compose -f docker-compose.test.yml run --rm acceptance


Via Local Environment
~~~~~~~~~~~~~~~~~~~~~

1. Select the virtualenv of your INSPIRE project:

.. code-block:: bash

  workon name_of_your_inspire_virtual_env

2. Go into the root directory of INSPIRE project:

.. code-block:: bash

  (inspirehep)$ cdvirtualenv src/inspirehep/

3. Run all the services with ``honcho``:

.. code-block:: bash

  (inspirehep)$ honcho start

4. Install Firefox

5. Open a new console and inside the same directory run the tests:

.. code-block:: bash

  (inspirehep)$ SERVER_NAME="http://localhost:5000" py.test --driver Firefox --html=selenium-report.html tests/acceptance
