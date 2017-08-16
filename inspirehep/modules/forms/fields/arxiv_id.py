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

from wtforms import TextField

from ..field_base import INSPIREField
from ..filter_utils import strip_prefixes, strip_string
from ..validators import arxiv_syntax_validation

__all__ = ['ArXivField']


class ArXivField(INSPIREField, TextField):
    def __init__(self, **kwargs):
        defaults = dict(
            icon='barcode',
            validators=[arxiv_syntax_validation],
            # Should have the same logic as stripSourceTags()
            # in literature_submission_form.js
            filters=[
                strip_string,
                strip_prefixes("arxiv:", "arXiv:"),
            ],
            description="e.g. hep-th/9711200 or 1207.7235 or arXiv:1001.4538",
            widget_classes="form-control"
        )
        defaults.update(kwargs)
        super(ArXivField, self).__init__(**defaults)
