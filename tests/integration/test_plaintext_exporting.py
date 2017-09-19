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

from inspirehep.utils.record_getter import get_es_record
import pytest
from inspirehep.modules.records.serializers.cvformattext_serializer import CVTextSerializer


@pytest.fixture
def request_context(app):
    with app.test_request_context() as context:
        yield context


def test_format_cv_plaintext(request_context):
    article = get_es_record('lit', 4328)
    expected = u"""Partial Symmetries of Weak Interactions.
By S. L. Glashow.
10.1016/0029-5582(61)90469-2.
Nucl.Phys. 22 (1961) 579-588.\n"""

    result = CVTextSerializer().create_bibliography([article])

    assert expected == result


def test_format_cv_plaintext_collab(request_context):
    article = get_es_record('lit', 1496635)
    expected = u"""Measurement of the CKM angle $\\gamma$ from a combination of LHCb results.
By R. Aaij et al. [LHCb Collaboration].
[arXiv:1611.03076 [hep-ex]].\n"""

    result = CVTextSerializer().create_bibliography([article])

    assert expected == result
