Harvesting
==========

1. About
--------

This document specifies how to harvest records into your system.


2. Prerequisites (optional)
---------------------------

If you are going to run harvesting workflows which needs prediction models such as the CORE guessing, keyword extraction, and plot extraction you may need to install some extra packages.

For example, on Ubuntu/Debian you could execute:

.. code-block:: bash

    (inspire)$ sudo aptitude install -y libblas-dev liblapack-dev gfortran imagemagick

For guessing, you need to point to a Beard Web service.

For keyword extraction using Magpie, you need to point to a Magpie Web service.

For hepcrawl crawling of sources via scrapy, you need to point to a scrapyd web service running `hepcrawl` project.


3. Quick start
--------------

All harvesting of scientific articles (hereafter "records") into INSPIRE consist of two steps:

  1. Downloading meta-data/files of articles from source and generating INSPIRE style meta-data.
  2. Each meta-data record is then taken through an ingestion workflow for pre- and post-processing.

Many records require human acceptance in order to be uploaded into the system. This is done via the Holding Pen web interface located at http://localhost:5000/holdingpen


3.1. Getting records from arXiv.org
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest way to get records into your system is to harvest from arXiv.org using OAI-PMH.

To do this we use `invenio-oaiharvester` CLI tool `inspirehep oaiharvester`. This will trigger a signal when records are harvested and `inspirehep` listens for this signal and starts harvesting workflows.

**Currently, this simple harvesting only works for arXiv records due to the need to convert the metadata to our format.**

Single records like this:

.. code-block:: bash

    (inspire)$ inspirehep oaiharvester harvest -u http://export.arxiv.org/oai2 -m arXiv -i oai:arXiv.org:1604.05726


Range of records like so:

.. code-block:: bash

    (inspire)$ inspirehep oaiharvester harvest -u http://export.arxiv.org/oai2 -m arXiv -f 2016-05-01 -t 2016-05-04 -s 'physics:hep-lat'

You can now see from your Celery logs that tasks are started and workflows are executed. Visit the Holding Pen interface, at http://localhost:5000/holdingpen to find the records and to approve/reject them. Once approved, they are queued for upload into the system.

3.2. Getting records from other sources (hepcrawl)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the full INSPIRE harvesting experience, you can use the hepcrawl service to get records into your system.

It works by scheduling crawls via certain triggers in `inspirehep` to a `scrapyd` service which then returns harvested records and ingestion workflows are triggered.

First make sure you have setup a scrapyd service running hepcrawl (TODO add link) and flower (workermon) running (done automatic with `honcho`).

In your local config (`${VIRTUAL_ENV}/var/inspirehep-instance/inspirehep.cfg`) add the following configuration:

.. code-block:: python

    CRAWLER_HOST_URL = "http://localhost:6800"   # replace with your scrapyd service
    CRAWLER_SETTINGS = {
        "API_PIPELINE_URL": "http://localhost:5555/api/task/async-apply",   # URL to your flower instance
        "API_PIPELINE_TASK_ENDPOINT_DEFAULT": "inspire_crawler.tasks.submit_results"
    }

Now you are ready to trigger harvests. There are two options on how to trigger harvests; `oaiharvester` like in 3.1 or trigger via shell/CLI (TODO).

Via OAI-PMH:

.. code-block:: bash

    (inspire)$ inspirehep oaiharvester harvest -u http://export.arxiv.org/oai2 -m arXiv -i oai:arXiv.org:1604.05726 -a spider=arXiv -a workflow=arxiv_ingestion

Note the two extra arguments which tells which spider to use to harvest the source in `hepcrawl`, and workflow which says which ingestion workflow to run upon receiving harvested records from the crawler.

If your scrapyd service is running you should see output appear from it shortly after harvesting. You can also see from your Celery logs that tasks are started and workflows are executed. Visit the Holding Pen interface, at http://localhost:5000/holdingpen to find the records and to approve/reject them. Once approved, they are queued for upload into the system.
