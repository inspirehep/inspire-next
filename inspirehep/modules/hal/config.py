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

"""HAL configuration."""

from __future__ import absolute_import, division, print_function


#
# Configuration used when converting to TEI.
#

HAL_DOMAIN_MAPPING = {
    'Accelerators': 'phys.phys.phys-acc-ph',
    'Astrophysics': 'phys.astr',
    'Computing': 'info',
    'Data Analysis and Statistics': 'phys.phys.phys-data-an',
    'Experiment-HEP': 'phys.hexp',
    'Experiment-Nucl': 'phys.nexp',
    'General Physics': 'phys.phys.phys-gen-ph',
    'Gravitation and Cosmology': 'phys.grqc',
    'Instrumentation': 'phys.phys.phys-ins-det',
    'Lattice': 'phys.hlat',
    'Math and Math Physics': 'phys.mphy',
    'Other': 'phys',
    'Phenomenology-HEP': 'phys.hphe',
    'Theory-HEP': 'phys.hthe',
    'Theory-Nucl': 'phys.nucl',
}
"""Mapping used when converting from INSPIRE categories to HAL domains."""


#
# Configuration used when connecting to HAL.
#

HAL_COL_IRI = 'https://api-preprod.archives-ouvertes.fr/sword/hal'
"""IRI used by the SWORD protocol when creating a new record on HAL.

Note:

    Use this to send records to their staging instance. To send records to
    their production instance use the same IRI without ``-preprod``.

"""

HAL_EDIT_IRI = 'https://api-preprod.archives-ouvertes.fr/sword/'
"""IRI used by the SWORD protocol when updating an existing record on HAL.

Note:

    Use this to update records on their staging instance. To update records
    on their production instance use the same IRI without ``-preprod``.

"""

HAL_USER_NAME = 'hal_user_name'
"""Name of the INSPIRE user on HAL.

Note:

    Its real value is stored in ``tbag``. In particular ``QA_HAL_USER_NAME``
    contains the value to use for their staging instance, while
    ``PROD_HAL_USER_NAME`` contains the value to use for their production
    instance.

"""

HAL_USER_PASS = 'hal_user_pass'
"""Password of the INSPIRE user on HAL.

Note:

    Its real value is stored in ``tbag``. In particular ``QA_HAL_USER_PASS``
    contains the value to use for their staging instance, while
    ``PROD_HAL_USER_PASS`` contains the value to use for their production
    instance.

"""

HAL_IGNORE_CERTIFICATES = False
"""Whether to check certificates when connecting to HAL."""
