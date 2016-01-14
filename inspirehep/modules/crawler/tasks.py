# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Celery tasks for dealing with crawler."""

import os
import json

from urlparse import urlparse

from flask import current_app

from invenio_ext.sqlalchemy import db
from invenio_celery import celery
from invenio_workflows.api import start_delayed

from .errors import (
    CrawlerScheduleError,
    CrawlerInvalidResultsPath,
    CrawlerJobVerificationError,
)
from .models import CrawlerJob


@celery.task(ignore_results=True)
def submit_results(job_id, results_uri, **kwargs):
    """Check results for current job."""
    results_path = urlparse(results_uri).path
    if not os.path.exists(results_path):
        raise CrawlerInvalidResultsPath(
            "Path specificed in result does not exist: {0}".format(results_path)
        )
    job = CrawlerJob.query.get(job_id)
    if not job:
        raise CrawlerJobVerificationError(
            "Cannot find job id: {0}".format(job_id)
        )
    with open(results_path) as records:
        for line in records:
            record = json.loads(line)
            start_delayed(job.workflow, data=[record], **kwargs)
            break


@celery.task(ignore_results=True)
def schedule_crawl(spider, workflow, **kwargs):
    """Schedule a crawl using configuration from the workflow objects."""
    from inspirehep.modules.crawler.utils import get_crawler_instance

    crawler = get_crawler_instance()
    crawler_settings = current_app.config.get('CRAWLER_SETTINGS')
    crawler_settings.update(kwargs.get("crawler_settings", {}))

    crawler_arguments = kwargs
    crawler_arguments.update(
        current_app.config.get('CRAWLER_SPIDER_ARGUMENTS', {}).get(spider, {})
    )
    job_id = crawler.schedule(
        project=current_app.config.get('CRAWLER_PROJECT'),
        spider=spider,
        settings=crawler_settings,
        **crawler_arguments
    )
    if job_id:
        CrawlerJob.create(
            job_id=job_id,
            spider=spider,
            workflow=workflow,
        )
        db.session.commit()
        print("Scheduled job {0}".format(job_id))
    else:
        raise CrawlerScheduleError(
            "Could not schedule '{0}' spider for project '{1}'".format(
                spider, current_app.config.get('CRAWLER_PROJECT')
            )
        )
