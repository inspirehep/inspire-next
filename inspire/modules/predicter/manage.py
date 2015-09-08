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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Manage predicter INSPIRE module."""

from __future__ import print_function

import os
import sys

from invenio.base.globals import cfg

from invenio.ext.script import Manager

from .tasks import train as celery_train


manager = Manager(usage=__doc__)


@manager.option('--records', '-r', dest='records',
                help='Train the model from records from this file.')
@manager.option('--output', '-o', dest='output',
                help='Pickle the model to this file.')
@manager.option('--skip-categories', '-c', dest='skip_categories',
                action="store_true", help='Train using record categories',
                default=False)
@manager.option('--skip-astro', dest='skip_astro',
                action="store_true", help='Skip astro records.',
                default=False)
def train(records, output, skip_categories=False, skip_astro=False):
    """Train a set of records from the command line.

    Usage: inveniomanage predicter train -r /path/to/json -o model.pickle
    """
    if not records:
        print("Missing records!", file=sys.stderr)
        return

    if not os.path.isfile(records):
        print("{0} is not a file!".format(records), file=sys.stderr)
        return

    if os.path.basename(output) == output:
        # Only a relative name, prefix with config
        output = os.path.join(
            cfg.get("CLASSIFIER_MODEL_PATH", ""), output
        )
    else:
        output = os.path.abspath(output)

    # Make sure directories are created
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(output)

    # Check that location is writable
    if not os.access(os.path.dirname(output), os.W_OK):
        print("{0} is not writable file!".format(output), file=sys.stderr)
        return

    job = celery_train.delay(records, output, skip_categories, skip_astro)
    print("Scheduled job {0}".format(job.id))
