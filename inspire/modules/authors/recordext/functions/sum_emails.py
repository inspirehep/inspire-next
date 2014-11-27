# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2015 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.


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
