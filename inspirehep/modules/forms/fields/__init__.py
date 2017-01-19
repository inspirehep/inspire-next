# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014 - 2017 CERN.
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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Init."""

from __future__ import absolute_import, division, print_function

from wtforms.utils import unset_value

from .abstract import *
from .date import *
from .doi import *
from .file_upload import *
from .issn import *
from .jinja import *
from .journal import *
from .keywords import *
from .language import *
from .notes import *
from .pages_number import *
from .publisher import *
from .title import *
from .wtformsext import *
