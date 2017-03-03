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

from datetime import date

from inspirehep.utils.latex import Latex
from inspirehep.utils.record_getter import get_db_record

import pytest


@pytest.mark.xfail(reason='wrong output')
def test_format_latex_eu(app):
    article = get_db_record('lit', 4328)
    today = date.today().strftime('%d %b %Y')

    expected = u'''%\cite{Glashow:1961tr}
\\bibitem{Glashow:1961tr}
  S.~L.~Glashow,
  %``Partial Symmetries of Weak Interactions,''
  Nucl.\ Phys.\  {\\bf 22} (1961) 579.
  doi:10.1016/0029-5582(61)90469-2
  %%CITATION = doi:10.1016/0029-5582(61)90469-2;%%
  %11 citations counted in INSPIRE as of ''' + today
    result = Latex(article, 'latex_eu').format()

    assert expected == result


@pytest.mark.xfail(reason='wrong output')
def test_format_latex_us(app):
    article = get_db_record('lit', 4328)
    today = date.today().strftime('%d %b %Y')

    expected = u'''%\cite{Glashow:1961tr}
\\bibitem{Glashow:1961tr}
  S.~L.~Glashow,
  %``Partial Symmetries of Weak Interactions,''
  Nucl.\ Phys.\  {\\bf 22}, 579 (1961).
  doi:10.1016/0029-5582(61)90469-2
  %%CITATION = doi:10.1016/0029-5582(61)90469-2;%%
  %11 citations counted in INSPIRE as of ''' + today
    result = Latex(article, 'latex_us').format()

    assert expected == result
