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

from inspirehep.utils.record_getter import get_es_record
from inspirehep.modules.records.serializers.latexeu_serializer import LatexEUSerializer
from inspirehep.modules.records.serializers.latexus_serializer import LatexUSSerializer

import pytest


@pytest.fixture
def request_context(app):
    with app.test_request_context() as context:
        yield context


def test_format_latex_eu(request_context):
    article = get_es_record('lit', 4328)
    today = date.today().strftime('%-d %b %Y')

    expected = u'''%\cite{Glashow:1961tr}
\\bibitem{Glashow:1961tr}
  S.~L.~Glashow,
  %``Partial Symmetries of Weak Interactions,''
  Nucl.\ Phys.\  {\\bf 22} (1961) 579.
  doi:10.1016/0029-5582(61)90469-2
  %%CITATION = DOI:10.1016/0029-5582(61)90469-2;%%
  %0 citations counted in INSPIRE as of ''' + today

    result = LatexEUSerializer().create_bibliography([article])

    assert expected == result


def test_format_latex_us(request_context):
    article = get_es_record('lit', 4328)
    today = date.today().strftime('%-d %b %Y')

    expected = u'''%\cite{Glashow:1961tr}
\\bibitem{Glashow:1961tr}
  S.~L.~Glashow,
  %``Partial Symmetries of Weak Interactions,''
  Nucl.\ Phys.\  {\\bf 22}, 579 (1961).
  doi:10.1016/0029-5582(61)90469-2
  %%CITATION = DOI:10.1016/0029-5582(61)90469-2;%%
  %0 citations counted in INSPIRE as of ''' + today

    result = LatexUSSerializer().create_bibliography([article])

    assert expected == result


def test_format_latex_eu_thesis(request_context):
    article = get_es_record('lit', 1395663)
    today = date.today().strftime('%-d %b %Y')

    expected = ur'''%\cite{Mankuzhiyil:2010jpa}
\bibitem{Mankuzhiyil:2010jpa}
  N.~Mankuzhiyil,
  %``MAGIC $\gamma$-ray observations of distant AGN and a study of source variability and the extragalactic background light using FERMI and air Cherenkov telescopes,''
  %0 citations counted in INSPIRE as of ''' + today

    result = LatexEUSerializer().create_bibliography([article])

    assert expected == result


def test_format_latex_us_thesis(request_context):
    article = get_es_record('lit', 1395663)
    today = date.today().strftime('%-d %b %Y')

    expected = ur'''%\cite{Mankuzhiyil:2010jpa}
\bibitem{Mankuzhiyil:2010jpa}
  N.~Mankuzhiyil,
  %``MAGIC $\gamma$-ray observations of distant AGN and a study of source variability and the extragalactic background light using FERMI and air Cherenkov telescopes,''
  %0 citations counted in INSPIRE as of ''' + today

    result = LatexUSSerializer().create_bibliography([article])

    assert expected == result
