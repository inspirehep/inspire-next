..
    This file is part of INSPIRE.
    Copyright (C) 2016 CERN.

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


Building this docs page
========================

Sometimes when you modify the docs it's convenient to generate them locally in
order to check them before sending a pull request, to do so, you'll have to
install some extra dependencies:


.. note::

    Remember that you'll need a relatively newer version of setuptools and
    pip, so if you just created a virtualenv for the docs, you might have to
    run:

    .. code-block:: console

        (inspirehep_docs)$ pip install --upgrade setuptools pip

    Also keep in mind that you need all the inspire system dependecies
    installed too, if you don't have them, go to Installation_

.. code-block:: console

    (inspirehep_docs)$ pip install -e .[all]

And then, you can generate the html docs pages with:

.. code-block:: console

    (inspirehep_docs)$ make -C docs html

And to view them, you can just open them in your favourite browser:

.. code-block:: console

    (enspirehep_docs)$ firefox docs/_build/html/index.html


.. _Installation: installation.html
