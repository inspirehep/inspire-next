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

"""Configuration for crawler integration."""

from invenio_oaiharvester.signals import oaiharvest_finished
from invenio_oaiharvester.utils import write_to_dir

from .tasks import schedule_crawl


@oaiharvest_finished.connect
def receive_oaiharvest_job(request, records, name, **kwargs):
    """Receive a list of harvested OAI-PMH records and schedule crawls."""
    spider = kwargs.get('spider')
    workflow = kwargs.get('workflow')
    if not spider or not workflow:
        return

    files_created, _ = write_to_dir(records)

    for source_file in files_created:
        schedule_crawl(spider, workflow, source_file=source_file)


__all__ = (
    'receive_oaiharvest_job',
)
