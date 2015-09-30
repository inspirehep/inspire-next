# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Update OAI Harvest configs."""

from sqlalchemy.orm.exc import NoResultFound


depends_on = []


def info():
    """Return description."""
    return __doc__


def do_upgrade():
    """Implement your upgrades here."""
    from invenio.ext.sqlalchemy import db
    from invenio_oaiharvester.models import OaiHARVEST

    # Change arXiv harvest workflow
    try:
        arxiv_task = OaiHARVEST.query.filter(
            OaiHARVEST.workflows == "ingestion_arxiv_math"
        ).one()
    except NoResultFound:
        return
    if arxiv_task:
        arxiv_task.workflows = "process_record_arxiv"
        db.session.add(arxiv_task)
        db.session.commit()

    # Remove legacy configs
    OaiHARVEST.query.filter(
        OaiHARVEST.workflows == "oaiharvest_harvest_repositories"
    ).delete()


def estimate():
    """Estimate running time of upgrade in seconds (optional)."""
    return 1


def pre_upgrade():
    """Run pre-upgrade checks (optional)."""
    pass


def post_upgrade():
    """Run post-upgrade checks (optional)."""
    pass
