GROBID
======

1. About
--------

This document specifies how to train and use GROBID.


2. Prerequisites
----------------

GROBID uses Maven as its build system. To install it on Debian/Ubuntu systems
we just have to type:

.. code-block:: bash

    $ sudo apt-get install maven

Note that this will also install Java, the language GROBID is written in.
Similar commands apply to other distributions. In particular for OS X we have:

.. code-block:: bash

    $ brew install maven


3. Quick start
--------------

To install GROBID we first need to clone its code:

.. code-block:: bash

    $ git clone https://github.com/inspirehep/grobid

Note that we are fetching it from our fork instead of the main repository
because our HEP training data has not yet been merged inside of it.
Now we move inside its ``grobid-service`` folder and start the service:

.. code-block:: bash

    $ cd grobid/grobid-service
    $ mvn jetty:run-war

This will run the tests, load the modules and start a service available at
``localhost:8080``.


4. Training
-----------

The models available after cloning are not using the new available training
data. To generate the new ones we need to go inside of the root folder and
call:

.. code-block:: bash

    $ cd grobid
    $ java -Xmx1024m -jar grobid-trainer/target/grobid-trainer-0.3.4-SNAPSHOT.one-jar.jar 0 $MODEL -gH grobid-home

where ``$MODEL`` is the model we want to train. Note that there's new data
only for the ``segmentation`` and ``header`` models.

Moreover, note that the ``0`` parameter instructs GROBID to only train the
models. A value of ``1`` will only evaluate the trained model on a random
subset of the data, while a value of ``2`` requires an additional parameter:

.. code-block:: bash

    $ java -Xmx1024m -jar grobid-trainer/target/grobid-trainer-0.3.4-SNAPSHOT.one-jar.jar 0 $MODEL -gH grobid-home -s$SPLIT

where ``$SPLIT`` is a float between 0 and 1 that represents the ratio of
data to be used for training.
