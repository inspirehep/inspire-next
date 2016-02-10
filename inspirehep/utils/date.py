# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Helpers for handling dates."""

import six

from invenio_utils.date import strftime, strptime   # pre-1900 friendly parser

DATE_FORMATS_YEAR = ["%Y", "%y"]
DATE_FORMATS_MONTH = [
    "%Y-%m", "%Y %b", "%b %Y", "%Y %B", "%B %Y",
    "%y-%m", "%y %b", "%b %y", "%y %B", "%B %y",
]
DATE_FORMATS_FULL = [
    "%Y-%m-%d", "%d %m %Y", "%x", "%d %b %Y",
    "%d %B %Y", "%d %b %y", "%d %B %y",
]


def create_earliest_date(dates):
    """Return the earliest valid date from a list of date strings."""
    if not dates:
        return None
    if not isinstance(dates, (list, set)):
        dates = [dates]
    valid_dates = []
    for date in dates:
        # Add 99 to the end of partial date to make sure we get the REAL
        # earliest date
        valid_date = create_valid_date(date,
                                       date_format_month="%Y-%m-99",
                                       date_format_year="%Y-99-99")
        if valid_date:
            valid_dates.append(valid_date)
    if valid_dates:
        date = min(valid_dates)
        return date.replace('-99', '')


def create_valid_date(date, date_format_full="%Y-%m-%d",
                      date_format_month="%Y-%m", date_format_year="%Y"):
    """Iterate over possible formats and return a valid date if found."""
    valid_date = None
    date = six.text_type(date)
    for format in DATE_FORMATS_FULL:
        try:
            valid_date = strftime(date_format_full, (strptime(date, format)))
            break
        except ValueError:
            pass
    else:
        for format in DATE_FORMATS_MONTH:
            try:
                if date.count('-') > 1:
                    date = "-".join(date.split('-')[:2])
                valid_date = strftime(date_format_month, (strptime(date, format)))
                break
            except ValueError:
                pass
        else:
            for format in DATE_FORMATS_YEAR:
                try:
                    if date.count('-') > 0:
                        date = date.split('-')[0]
                    valid_date = strftime(date_format_year, (strptime(date, format)))
                    break
                except ValueError:
                    pass
    return valid_date


def create_datestruct(datetext):
    """
    Create a datestruct out of a date text in format YYYY-MM-dd
    :param datetext: date from record
    :type datetext: str
    :returns: tuple of 1 or more integers, up to max (year, month, day).
        Otherwise None.
    """
    if isinstance(datetext, int):
        datetext = unicode(datetext)
    if not datetext or not isinstance(datetext, six.string_types):
        return None
    datetext = datetext.strip()
    return tuple([int(component) for component in datetext.split('-')])
