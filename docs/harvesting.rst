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


Harvesting
==========

1. About
--------

This document specifies how to harvest records into your system.


2. Prerequisites (optional)
---------------------------

If you are going to run harvesting workflows which needs prediction models such as the CORE guessing, keyword extraction, and plot extraction you may need to install some extra packages.

.. warning::

    Those additional services (i.e. Beard and Magpie) are not Dockerized, so you will have to do
    that yourself if the need arises. Instructions below are only applicable if you're running
    inspire locally, without Docker.

For example, on Ubuntu/Debian you could execute:

.. code-block:: bash

    (inspire)$ sudo aptitude install -y libblas-dev liblapack-dev gfortran imagemagick

For guessing, you need to point to a Beard Web service with the config variable
``BEARD_API_URL``.

For keyword extraction using Magpie, you need to point to a Magpie Web service with the config variable
``MAGPIE_API_URL``.

For hepcrawl crawling of sources via scrapy, you need to point to a scrapyd web service running `hepcrawl` project.

More info at http://pythonhosted.org/hepcrawl/


3. Quick start
--------------

All harvesting of scientific articles (hereafter "records") into INSPIRE consist of two steps:

  1. Downloading meta-data/files of articles from source and generating INSPIRE style meta-data.
  2. Each meta-data record is then taken through an ingestion workflow for pre- and post-processing.

Many records require human acceptance in order to be uploaded into the system. This is done via the Holding Pen web interface located at http://localhost:5000/holdingpen


3.1. Getting records from arXiv.org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Firstly, in order to start harvesting records you will need to deploy the spiders, if you are
using docker:

.. code-block:: console

    docker compose -f docker-compose.deps.yml run --rm scrapyd-deploy

The simplest way to get records into your system is to harvest from arXiv.org using OAI-PMH.

To do this we use `inspire-crawler` CLI tool ``inspirehep crawler``.

See `the diagram in hepcrawl documentation <https://pythonhosted.org/hepcrawl/inspire_crawler.html>`_
to see what happens behind the scenes.

Single records like this (if you are running docker, you first will need to open bash and get into
the virtual environment in one of the workers, e.g. ``docker compose run --rm web bash``, read the
:ref:`other_sources` section if you aren't using docker):

.. code-block:: bash

    (inspire)$ inspirehep crawler schedule arXiv_single article \
        --kwarg 'identifier=oai:arXiv.org:1604.05726'


Range of records like so:

.. code-block:: bash

    (inspire)$ inspirehep crawler schedule arXiv article \
        --kwarg 'from_date=2016-06-24' \
        --kwarg 'until_date=2016-06-26' \
        --kwarg 'sets=physics:hep-th'

You can now see from your Celery logs that tasks are started and workflows are executed. Visit the Holding Pen interface, at http://localhost:5000/holdingpen to find the records and to approve/reject them. Once approved, they are queued for upload into the system.

.. _other_sources:

3.2. Getting records from other sources (no Docker)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example above shows in the simplest case how you can use `hepcrawl` to harvest Arxiv, however
hepcrawl can harvest any source so long as it has a spider for that source.

It works by scheduling crawls via certain triggers in `inspirehep` to a `scrapyd` service which then returns harvested records and ingestion workflows are triggered.

First make sure you have setup a scrapyd service running hepcrawl (http://pythonhosted.org/hepcrawl/operations.html) and flower (workermon) running (done automatic with `honcho`).

In your local config (`${VIRTUAL_ENV}/var/inspirehep-instance/inspirehep.cfg`) add the following configuration:

.. code-block:: python

    CRAWLER_HOST_URL = "http://localhost:6800"   # replace with your scrapyd service
    CRAWLER_SETTINGS = {
        "API_PIPELINE_URL": "http://localhost:5555/api/task/async-apply",   # URL to your flower instance
        "API_PIPELINE_TASK_ENDPOINT_DEFAULT": "inspire_crawler.tasks.submit_results"
    }

Now you are ready to trigger harvests. There are two options on how to trigger harvests, from the
CLI or code.

Via shell:

.. code-block:: python

    from inspire_crawler.tasks import schedule_crawl
    schedule_crawl(spider, workflow, **kwargs)

Via inspirehep cli:

.. code-block:: bash

    (inspire)$ inspirehep crawler schedule --kwarg 'sets=hep-ph,math-ph' --kwarg 'from_date=2018-01-01' arXiv article

If your scrapyd service is running you should see output appear from it shortly after harvesting.
You can also see from your Celery logs that tasks are started and workflows are executed. Visit
the Holding Pen interface, at http://localhost:5000/holdingpen to find the records and to
approve/reject them. Once approved, they are queued for upload into the system.


3.2. Getting records from other sources (with Docker)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It works by scheduling crawls via certain triggers in `inspirehep` to a `scrapyd` service which then returns harvested records and ingestion workflows are triggered.

Scrapyd service and configuration for inspire-next will be automatically set up by docker-compose,
so you don't have to worry about it.

If you have not previously deployed your spiders, you will have to do it like so:

.. code-block:: console

    docker compose -f docker-compose.deps.yml run --rm scrapyd-deploy

Afterwards you can schedule a harvest from the CLI or shell:

.. code-block:: python

    from inspire_crawler.tasks import schedule_crawl
    schedule_crawl(spider, workflow, **kwargs)

Via inspirehep cli:

.. code-block:: bash

    (inspire docker)$ inspirehep crawler schedule arXiv article --kwarg 'sets=hep-ph,math-ph' --kwarg 'from_date=2018-01-01'

Where `arXiv` is any spider in
`hepcrawl/spiders/ <https://github.com/inspirehep/hepcrawl/tree/master/hepcrawl/spiders>`_ and each
of the ``kwarg``s is a parameter to the spiders ``__init__``.
