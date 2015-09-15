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


def get_persistent_identifiers_keys(keys):
    """According with @persistent_identifier it recollects all the fields that
    could be considered as persistent identifiers
    """
    from invenio.modules.jsonalchemy.reader import FieldParser

    def smart_set_element(the_list, index, value):
        try:
            the_list[index] = value
        except IndexError:
            for i in xrange(len(the_list), index + 1):
                the_list.append(None)
            the_list[index] = value

    tmp = []
    for key in keys:
        try:
            if FieldParser.field_definitions[key]['persistent_identifier'] is not None:
                smart_set_element(tmp, FieldParser.field_definitions[key]['persistent_identifier'], key)
        except TypeError:
            # Work arround for [0] and [n]
            for kkey in FieldParser.field_definitions[key]:
                if FieldParser.field_definitions[kkey]['persistent_identifier']:
                    smart_set_element(tmp, FieldParser.field_definitions[key]['persistent_identifier'], key)
        except:
            continue

    return filter(None, tmp)
