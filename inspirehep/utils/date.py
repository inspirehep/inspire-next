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

"""Helpers for handling dates before 1900."""

import six
import re
import time

from datetime import date as real_date
from datetime import datetime as real_datetime

from flask_babelex import format_datetime as babel_format_datetime

# This library does not support strftime's "%s" or "%y" format strings.
# Allowed if there's an even number of "%"s because they are escaped.
_illegal_formatting = re.compile(r"((^|[^%])(%%)*%[sy])")

DATE_FORMATS_YEAR = ["%Y", "%y"]
DATE_FORMATS_MONTH = [
    "%Y-%m", "%Y %b", "%b %Y", "%Y %B", "%B %Y",
    "%y-%m", "%y %b", "%b %y", "%y %B", "%B %y",
]
DATE_FORMATS_FULL = [
    "%Y-%m-%d", "%d %m %Y", "%x", "%d %b %Y",
    "%d %B %Y", "%d %b %y", "%d %B %y",
]


class date(real_date):

    def strftime(self, fmt):
        return strftime(fmt, self)


class datetime(real_datetime):

    def strftime(self, fmt):
        return strftime(fmt, self)

    @classmethod
    def combine(self, date, time):
        return self(date.year, date.month, date.day, time.hour, time.minute,
                    time.second, time.microsecond, time.tzinfo)

    def __add__(self, other):
        d = real_datetime.combine(self, self.timetz())
        d += other
        return self.combine(d, d.timetz())

    def date(self):
        return date(self.year, self.month, self.day)

    @staticmethod
    def strptime(date_string, format):
        return datetime(*(time.strptime(date_string, format)[0:6]))


def _findall(text, substr):
    # Also finds overlaps
    sites = []
    i = 0
    while True:
        j = text.find(substr, i)
        if j == -1:
            break
        sites.append(j)
        i = j + 1
    return sites


def strftime(fmt, dt):
    if not isinstance(dt, real_date):
        dt = datetime(dt.tm_year, dt.tm_mon, dt.tm_mday, dt.tm_hour, dt.tm_min,
                      dt.tm_sec)
    if dt.year >= 1900:
        return time.strftime(fmt, dt.timetuple())
    illegal_formatting = _illegal_formatting.search(fmt)
    if illegal_formatting:
        raise TypeError("strftime of dates before 1900 does not handle %s" %
                        illegal_formatting.group(0))

    year = dt.year
    # For every non-leap year century, advance by
    # 6 years to get into the 28-year repeat cycle
    delta = 2000 - year
    off = 6 * (delta // 100 + delta // 400)
    year = year + off

    # Move to around the year 2000
    year = year + ((2000 - year) // 28) * 28
    timetuple = dt.timetuple()
    s1 = time.strftime(fmt, (year,) + timetuple[1:])
    sites1 = _findall(s1, str(year))

    s2 = time.strftime(fmt, (year + 28,) + timetuple[1:])
    sites2 = _findall(s2, str(year + 28))

    sites = []
    for site in sites1:
        if site in sites2:
            sites.append(site)

    s = s1
    syear = "%04d" % (dt.year,)
    for site in sites:
        s = s[:site] + syear + s[site + 4:]
    return s


def strptime(date_string, fmt):
    return real_datetime(*(time.strptime(date_string, fmt)[:6]))


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


def convert_datestruct_to_dategui(datestruct, ln=None, output_format="d MMM Y, H:mm"):
    """Convert: (2005, 11, 16, 15, 11, 44, 2, 320, 0) => '16 nov 2005, 15:11'
    Month is internationalized
    """
    assert ln is None, 'setting language is not supported'
    try:
        if datestruct[0] and datestruct[1] and datestruct[2]:
            dt = datetime.fromtimestamp(time.mktime(datestruct))
            return babel_format_datetime(dt, output_format)
        else:
            raise ValueError
    except:
        return _("N/A")


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
