Harvesting
==========

1. About
--------

This document specifies how to harvest records into your system.


2. Prerequisites
----------------

If you are going to run harvesting workflows which needs prediction models such as the CORE guessing, you need to install some extra packages.

For example, on Ubuntu/Debian you could execute:

.. code-block:: bash

    (inspire)$ sudo aptitude install -y libblas-dev liblapack-dev gfortran imagemagick

Then to install the requirements:

.. code-block:: bash

    (inspire)$ cdvirtualenv src/inspire-next
    (inspire)$ pip install -r requirements-harvesting.txt --exists-action i


3. Quick start
--------------

3.1. Getting records from inspirehep.net
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to get records into your system is to harvest them from our production site `http://inspirehep.net <http://inspirehep.net>`_ via OAI-PMH.


To fetch records via their INSPIRE record identifier:

.. code-block:: console

    $ inveniomanage oaiharvester get -n inspire_prod_sync -o workflow -i oai:inspirehep.net:1222902

To fetch a series of records for a collection, in this case HEP records updated within a date-range:

    $ inveniomanage oaiharvester get -n inspire_prod_sync -o workflow -f 2015-09-01 -t 2015-09-02 -s "INSPIRE:HEP"


See `invenio-oaiharvester <https://invenio-oaiharvester.readthedocs.org/en/latest/>`_ for more info.

4. Prediction models
--------------------

4.1. Training models
~~~~~~~~~~~~~~~~~~~~

Here is how to train the model from scratch:

.. code-block:: bash

    (inspire)$ inveniomanage classifier train -r /path/to/trainingset.json -o core_guessing.pickle

You will need the correct trainingset in order to perform the training.

TODO: Add link to trainingset
TODO: Add overview of current prediction models

You can use an existing pickled model file (not recommended):

.. code-block:: bash

    (inspire)$ cdvirtualenv var/data/classifier/models/
    (inspire)$ cp /path/to/yourmodel.pickle .
