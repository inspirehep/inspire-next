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
from inspirehep import config

import pytest

from inspirehep.modules.records.serializers.cvformatlatex_serializer import CVLatexSerializer
from inspirehep.utils.record_getter import get_es_record


@pytest.fixture
def request_context(app):
    with app.test_request_context() as context:
        yield context


def test_format_cv_latex(request_context):
    article = get_es_record('lit', 4328)
    today = date.today().strftime('%-d %b %Y')

    expected = ur'''%\cite{Glashow:1961tr}
\item%{Glashow:1961tr}
{\bf ``Partial Symmetries of Weak Interactions''}
  \\{}S.~L.~Glashow.
  \\{}10.1016/0029-5582(61)90469-2
  \\{}Nucl.\ Phys.\  {\bf 22}, 579 (1961).
 %\href{http://''' + config.SERVER_NAME + u'''/record/4328}{HEP entry}.
 %0 citations counted in INSPIRE as of ''' + today

    result = CVLatexSerializer().create_bibliography([article])

    assert expected == result


def test_format_cv_latex_collab(request_context):
    article = get_es_record('lit', 1496635)
    today = date.today().strftime('%-d %b %Y')

    expected = ur'''%\cite{Aaij:2016kjh}
\item%{Aaij:2016kjh}
{\bf ``Measurement of the CKM angle $\gamma$ from a combination of LHCb results''}
  \\{}R.~Aaij {\it et al.} [LHCb Collaboration].
  \\{}[arXiv:1611.03076 [hep-ex]].
 %\href{http://''' + config.SERVER_NAME + u'''/record/1496635}{HEP entry}.
 %1 citation counted in INSPIRE as of ''' + today

    result = CVLatexSerializer().create_bibliography([article])

    assert expected == result
