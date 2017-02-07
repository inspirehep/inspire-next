# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

from __future__ import absolute_import, division, print_function

from datetime import date

import pytest

from inspirehep.utils.cv_latex import Cv_latex
from inspirehep.utils.record_getter import get_db_record


@pytest.mark.xfail(reason='wrong output')
def test_format_cv_latex(app):
    article = get_db_record('lit', 4328)
    today = date.today().strftime('%d %b %Y')

    expected = u'''%\cite{Glashow:1961tr}
\item%{Glashow:1961tr}
{\\bf ``Partial Symmetries of Weak Interactions''}
  \{}S.~L.~Glashow.
  \{}10.1016/0029-5582(61)90469-2
  \{}Nucl.\ Phys.\  {\\bf 22}, 579 (1961).
%(1961)
%\href{http://inspirehep.net/record/4328}{HEP entry}
%11 citations counted in INSPIRE as of ''' + today
    result = Cv_latex(article).format()

    assert expected == result
