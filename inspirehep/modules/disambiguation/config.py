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

"""Disambiguation configuration."""

from __future__ import absolute_import, division, print_function


DISAMBIGUATION_SAMPLED_PAIRS_SIZE = 12 * 100000
"""The number of signature pairs we use during training.

Since INSPIRE has ~3M curated signatures it would take too much time
to train on all possible pairs, so we sample ~1M pairs in such a way
that they are representative of the known clusters structure.

Note:

    It MUST be a multiple of 12 for the reason explained in
    :mod:`inspirehep.modules.disambiguation.core.ml.sampling`.

"""
