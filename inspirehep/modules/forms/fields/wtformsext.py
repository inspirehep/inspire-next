# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

import wtforms

from ..field_base import InspireField

__all__ = []

for attr_name in dir(wtforms):
    attr = getattr(wtforms, attr_name)
    try:
        if issubclass(attr, wtforms.Field):
            # From a WTForm field, dynamically create a new class the same name
            # as the WTForm field (inheriting from InspireField() and the
            # WTForm field itself). Store the new class in the current module
            # with the same name as the WTForms.
            #
            # For further information please see Python reference documentation
            # for globals() and type() functions.
            globals()[attr_name] = type(
                str(attr_name),
                (InspireField, attr),
                {}
            )
            __all__.append(attr_name)
    except TypeError:
        pass
