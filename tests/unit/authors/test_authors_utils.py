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

from inspirehep.modules.authors.utils import bai


def test_that_bai_conforms_to_the_spec():
    assert bai("Ellis, Jonathan Richard") == "J.R.Ellis"
    assert bai("ellis, jonathan richard") == "J.R.Ellis"
    assert bai("ELLIS, JONATHAN RICHARD") == "J.R.Ellis"
    assert bai("Ellis, John Richard") == "J.R.Ellis"
    assert bai("Ellis, J R") == "J.R.Ellis"
    assert bai("Ellis, J. R.") == "J.R.Ellis"
    assert bai("Ellis, J.R.") == "J.R.Ellis"
    assert bai("Ellis, J.R. (Jr)") == "J.R.Ellis"
    assert bai("Ellis") == "Ellis"
    assert bai("Ellis, ") == "Ellis"
    assert bai("O'Connor, David") == "D.OConnor"
    assert bai("o'connor, david") == "D.OConnor"
    assert bai("McCurdy, David") == "D.McCurdy"
    assert bai("DeVito, Dany") == "D.DeVito"
    assert bai("DEVITO, Dany") == "D.Devito"
    assert bai("De Villiers, Jean-Pierre") == "J.P.de.Villiers"
    assert bai("Höing, Rebekka Sophie") == "R.S.Hoeing"
    assert bai("Müller, Andreas") == "A.Mueller"
