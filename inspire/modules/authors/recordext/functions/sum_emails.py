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


def sum_emails(self, public, current_private, old_private):
    """Get summed emails.

    :param public: Name of public emails field
    :param current_private: Name of current private emails field
    :param old_private: Name of old private emails field

    :return: ``List`` with emails and info about their privateness and status.
    """
    result = []
    if public in self:
        for email in self[public]:
            result.append(email)
            result[-1]['private'] = False
    if current_private in self:
        for email in self[current_private]:
            result.append(email)
            result[-1]['current'] = 'current'
            result[-1]['private'] = True
    if old_private in self:
        for email in self[old_private]:
            result.append(email)
            result[-1]['private'] = True

    return result
