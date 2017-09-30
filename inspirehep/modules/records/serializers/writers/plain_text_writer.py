# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

from . import PybtexBaseWriter
from flask import current_app


class PlainTextWriter(PybtexBaseWriter):
    """Outputs bibliography in plain text"""

    def get_template_src(self):
        return 'records/plaintext.txt'

    def process_entry(self, texkey, entry):
        """
        Preprocess values for display in the template.
        """
        fields = dict(entry.fields)
        template = super(PlainTextWriter, self).process_entry(texkey, entry)
        new_template = {
            'url': 'http://' + current_app.config['SERVER_NAME'] + '/record/' + fields['key'],
            'primaryClasses': fields.get('primaryClasses')
        }
        template.update(new_template)
        return template
