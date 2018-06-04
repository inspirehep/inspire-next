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

import pytest

from inspirehep.modules.disambiguation.core.ml.models import EthnicityEstimator

TRAINING_DATA = '''\
RACE,NAMELAST,NAMEFRST
1,EASTWOOD,CLINT
5,MIFUNE,TOSHIRO
'''


def test_ethnicity_estimator(tmpdir):
    input_file = tmpdir.join('input.csv')
    input_file.write(TRAINING_DATA)
    output_file = tmpdir.join('output.pkl')

    estimator = EthnicityEstimator()
    estimator.load(str(input_file))
    estimator.fit()
    estimator.save(str(output_file))


def test_ethnicity_estimator_methods_must_be_called_in_the_right_order(tmpdir):
    input_file = tmpdir.join('input.csv')
    input_file.write(TRAINING_DATA)
    output_file = tmpdir.join('output.pkl')

    estimator = EthnicityEstimator()
    with pytest.raises(ValueError) as excinfo:
        estimator.fit()
    assert '"load" before "fit"' in str(excinfo.value)
    estimator.load(str(input_file))
    with pytest.raises(ValueError) as excinfo:
        estimator.save(str(output_file))
    assert '"fit" before "save"' in str(excinfo.value)
    estimator.fit()
    estimator.save(str(output_file))
