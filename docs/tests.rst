..
    This file is part of INSPIRE.
    Copyright (C) 2015, 2016, 2017 CERN.

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


Inspire Tests
=============

How to Run the Selenium Tests
-----------------------------

Via Docker
~~~~~~~~~~

1. If you have not installed ``docker`` and ``docker-compose``, `install them now`_.

.. _install them now: https://github.com/inspirehep/inspire-next/pull/1015

2. Run ``docker``:

.. code-block:: bash

  $ docker-compose -f docker-compose.test.yml run --rm acceptance


Via Docker with a graphical instance of Firefox (Linux)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Check the first step in the `Via Docker`_ section.

2. Add the root user to the list allowed by **X11**:

.. code-block:: bash

  $ xhost local:root
  non-network local connections being added to access control list

3. Run ``docker``:

.. code-block:: bash

  $ docker-compose -f docker-compose.test.yml run --rm acceptance


Via Docker with a graphical instance of Firefox (macOS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Check the first step in the `Via Docker`_ section.

2. Install **XQuartz**: go to the `XQuartz website`_ and install the latest version.
   In alternative, run:

.. code-block:: bash

  $ brew cask install xquartz

.. _`XQuartz website`: https://www.xquartz.org/

3. Having installed **XQuartz**, run it and open the **XQuartz** ->
   **Preferences** menu from the bar. Go to the last tab, **Security**, enable
   both the **"Authenticate connections"** and **"Allow connections from network
   clients"** checkboxes, then restart your computer.

.. figure:: images/xquartz_security.jpg
  :align: center
  :alt: XQuartz security options we recommend.
  :scale: 45%

4. Write down the IP address of your computer because you will need it later:

.. code-block:: bash

  $ ifconfig en0 | grep inet | awk '$1=="inet" {print $2}'
  123.456.7.890

5. Add the IP address of your computer to the list allowed by **XQuartz**:

.. code-block:: bash

  $ xhost + 123.456.7.890
  123.456.7.890 being added to access control list

6. Set the ``$DISPLAY`` environment variable to the same IP address, followed by
   the id of your display (in this case, ``:0``):

.. code-block:: bash

  $ export DISPLAY=123.456.7.890:0

7. Run ``docker``:

.. code-block:: bash

  $ docker-compose -f docker-compose.test.yml run --rm acceptance
