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
#
"""BibFormat element - Prints document date
"""
from invenio.utils.date import convert_datestruct_to_dategui
import re

__revision__ = "$Id$"


def format_element(bfo, us="yes"):
    """
    Return dategui for the best available date.

    Looking in several locations for it (date, eprint, journal, date added).

    @param bfo: BibFormatObject for current record
    @type nfo: object

    @param us: us style date Mon dd, yyyy (default), otherwise dd mon yyyy
    @type us: str

    @return: string of formatted date, or None of no date is found.
    """
    datestruct = get_date(bfo)
    if datestruct:
        dummy_time = (0, 0, 44, 2, 320, 0)
        # if we have all 3 use dategui:
        if len(datestruct) == 3:
            datestruct = tuple(datestruct[0:3]) + dummy_time
            date = re.sub(',\s00:00$', '', convert_datestruct_to_dategui(datestruct))
            if us == "yes":
                return(re.sub(r' 0(\d),', r' \1,', (re.sub(r'(\d{2})\s(\w{3})', r'\2 \1,', date))))
            else:
                return(date)
        elif len(datestruct) == 2:
            # if we have only the month, pass the converter a dummy day and
            # then strip it
            datestruct = tuple(datestruct[0:2]) + (1,) + dummy_time
            date = re.sub(r',\s00:00$', '', convert_datestruct_to_dategui(datestruct))
            return re.sub(r'\d+\s+(\w+)', r'\1', date)
        elif len(datestruct) == 1:
            # only the year
            return datestruct[0]
    return None


def get_date(bfo):
    """
    Return datestruct for best available date. Returns None if none found.

    @param bfo: BibFormatObject for current record
    @type nfo: object

    @return: tuple of 1 or more integers, up to max (year, month, day).
        Otherwise None.
    """
    from bfe_inspire_arxiv import get_arxiv

    # true date
    date = bfo.fields('269__c')
    if date:
        datestruct = parse_date(date[0])
        if datestruct:
            return datestruct

    # arxiv date
    arxiv = get_arxiv(bfo, category="no")
    if arxiv:
        date = re.search('(\d+)', arxiv[0]).groups()[0]
        if len(date) >= 4:
            year = date[0:2]
            if year > '90':
                year = '19' + year
            else:
                year = '20' + year
            date = year + date[2:4] + '00'
            date = parse_date(date)
            if date:
                return date

    # journal year
    date = bfo.fields('773__y')
    if date:
        datestruct = parse_date(date[0])
        if datestruct:
            return datestruct

    # date added
    date = bfo.fields('961__x')
    if date:
        datestruct = parse_date(date[0])
        if datestruct:
            return datestruct

    # book year
    date = bfo.fields('260__c')
    if date:
        datestruct = parse_date(date[0])
        if datestruct:
            return datestruct

    # thesis date
    date = bfo.fields('502__d')
    if date:
        datestruct = parse_date(date[0])
        if datestruct:
            return datestruct

    return None


def parse_date(datetext):
    """
    Read in a date-string.

    Reads either native spires (YYYYMMDD) or invenio style (YYYY-MM-DD). Then as
    much of the date as we have is returned in a tuple.

    @param datetext: date from record
    @type datetext: str

    @return: tuple of 1 or more integers, up to max (year, month, day).
        Otherwise None.
    """
    if datetext in [None, ""] or type(datetext) != str:
        return None
    datetext = datetext.strip()
    datetext = datetext.split(' ')[0]
    datestruct = []
    if "-" in datetext:
        # Looks like YYYY-MM-DD
        for date in datetext.split('-'):
            if date:
                try:
                    datestruct.append(int(date))
                    continue
                except ValueError:
                    pass
            break
    else:
        # Looks like YYYYMMDD
        try:
            # year - YYYY
            year = datetext[:4]
            if year == "":
                return tuple(datestruct)
            datestruct.append(int(year))
            # month - MM
            month = datetext[4:6]
            if month == "":
                return tuple(datestruct)
            datestruct.append(int(month))
            day = datetext[6:8]
            # day - DD
            if day == "":
                return tuple(datestruct)
            datestruct.append(int(day))
        except ValueError:
            pass
    return tuple(datestruct)
