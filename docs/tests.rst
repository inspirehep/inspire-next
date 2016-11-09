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

How to Write Selenium Tests
---------------------------

Selenium Test Framework
~~~~~~~~~~~~~~~~~~~~~~~~
The framework that Inspire uses to run the End-To-End tests is called: `bat_framework` (`~/tests/acceptance`). This is the structure:

- `Pytest tests`
- `Page layer`
- `Arsenic` (Selenium Wrapper for INSPIRE)
- `Arsenic_Response`

.. figure:: images/BAT_Framework.png

Pytest tests
~~~~~~~~~~~~~~~~~~
This layer does not interact with Selenium directly. It interacts with the `page layer`. Each function inside this component should represent a test, and each test should be very short and readable.
Readable in this case means that the workflow that the test is executing should be clear. For instance:

.. code-block:: python

    def test_review_submission_author(login):
        create_author.go_to()
        create_author.submit_author(input_author_data)
        holding_panel_author_list.go_to()
        holding_panel_author_list.load_submitted_record(input_author_data)
        holding_panel_author_detail.go_to()
        holding_panel_author_detail.load_submitted_record(input_author_data)
        assert holding_panel_author_detail.review_record().has_error()




Page layer
~~~~~~~~~~~~~~~~~~
This layer is concretely a collection of python modules. Each module is representing a URI and it has the responsibility to interact with the page and give back some specific information. This part of the framework should not contain any assertion statement.

This layer interact directly with `Arsenic` and is the only one that is allowed to use it. The only exception has been done for the `conftest.py` file that has to initialise the framework.


Arsenic (Inspire Selenium Wrapper)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Arsenic has all the methods that Selenium usually exposes plus some specific methods for the INSPIRE webapp. A method has to be added to the Arsenic class when is going to use a component that is characteristic for the INSPIRE application. For instance: the procedure to use a datapicker or an autocompletion field should be putted in the Arsenic class.

This class is a singleton. This decision has been taken in order to write a more clean code. This allows to do not pass each time the selenium's object from the `Pytest test` to the `Page layer`.

Arsenic_Response
~~~~~~~~~~~~~~~~~
This object contains the test that the pytest function should run in order to understand if the task has been completed.
It is highly recommended to use the lambda function. This allows the framework to adapt the test in according to what should be tested in that specific use case.


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
