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

from inspirehep.utils.cv_latex_html_text import Cv_latex_html_text
from inspirehep.utils.record_getter import get_db_record


def test_format_cv_latex_html(app):
    record = get_db_record('lit', 4328)

    expected = (
        '<a href="localhost:5000/record/4328">Partial Symmetries of Weak Interactions.'
        '</a>,By S.L. Glashow.,<a href="http://dx.doi.org/10.1016/0029-5582(61)90469-2"'
        '>10.1016/0029-5582(61)90469-2</a>.,Nucl.Phys. 22 (1961) 579-588.,,')
    result = Cv_latex_html_text(record, 'cv_latex_html', ',').format()

    assert expected == result
