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

"""Function for correct representation of dates."""


def merged_dates(birth, death):
    """
    Helper function to merge dates of birth and death.

    :param birth: date of birth
    :param death: date of death
    """
    result = ""
    if birth:
        result += str(birth)
    result += "-"
    if death:
        result += str(death)
    return result if result != '-' else None
