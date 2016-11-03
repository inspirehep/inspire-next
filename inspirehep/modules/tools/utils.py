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
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""Utility functions for various tools."""

from __future__ import absolute_import, print_function

import re

import six
from nameparser import HumanName


def authorlist(text):
    """Call the relevant formatter depending on the existence of affiliations.

    Input can be in two different formats:
        F. Lastname, F.M. Otherlastname
    or
        F. Lastname1, F.M. Otherlastname1,2
        1 CERN
        2 Otheraffiliation
    """
    if not text:
        return ''
    if not isinstance(text, six.text_type):
        text = text.decode('utf-8')

    # Assume that if there are numbers in author name, they are affilation ids.
    # Also assume that if one author has an affiliation, everyone else has too.
    text = text.replace('\r', '')  # Input from the form contains unwanted \r's
    if re.search(r'\w+\d+', text):
        return authorlist_with_affiliations(text)

    return authorlist_without_affiliations(text)


def format_name(author):
    """Parse the raw author name and return a formatted string."""
    name = HumanName(author)
    # If there is only one part in the name, nameparser thinks it's a
    # first name. In reality, it is a last name, so we correct that.
    if name.first and not name.last:
        lname, mname, fname = name.first, name.middle, name.last
    else:
        fname, mname, lname = name.first, name.middle, name.last

    return u'{}{}{}'.format(
        lname,
        ', ' + fname if fname else '',
        ' ' + mname if mname else ''
    )


def authorlist_without_affiliations(text):
    """Return a MARC format string of authors without affiliations."""
    authors = text.split(', ')
    first_author = authors.pop(0)
    marc = u'100__ $$a{}\n'.format(format_name(first_author))
    for author in authors:
        marc += u'700__ $$a{}\n'.format(format_name(author))

    return marc.rstrip()


def authorlist_with_affiliations(text):
    """Return a MARC format string of authors with affiliations."""
    def parse_author_string(author):
        """Get fullname and affiliation ids."""
        try:
            name, affs = re.search(
                r'(.+?)(\d+\,*\d*)', author, flags=re.UNICODE
            ).groups()
        except AttributeError:
            raise
        fullname = format_name(name)
        aff_ids = affs.split(',')

        return fullname, aff_ids

    def create_new_marcline(author, affiliations, first_author=False):
        """Get MARC line of the format '100__ $$aDurães, F.$$vCERN'."""
        try:
            fullname, aff_ids = parse_author_string(author)
        except AttributeError:
            raise AttributeError('Cannot parse author name', author)
        try:
            affstring = ' '.join(
                [u'$$v{}'.format(affiliations[aff_id]) for aff_id in aff_ids]
            )
        except KeyError:
            raise KeyError('No affiliation with id', aff_ids, author)

        if first_author:
            marcfield = '100'
        else:
            marcfield = '700'

        return u'{}__ $$a{}{}\n'.format(marcfield, fullname, affstring)

    lines = [line for line in text.split('\n') if line]

    # Extract authors:
    authors = lines.pop(0)
    authors = authors.replace(' and ', ', ')
    authors = authors.split(', ')

    # Extract affiliations:
    affiliations = {}
    for aff in lines:
        try:
            key, value = aff.split(' ', 1)
            affiliations[key] = value
        except ValueError:
            raise ValueError('Cannot parse affiliation ', aff)

    try:
        first_author = authors.pop(0)
        marc = ''
        marc = create_new_marcline(
            first_author,
            affiliations,
            first_author=True
        )
        for author in authors:
            marc += create_new_marcline(author, affiliations)
    except (AttributeError, KeyError):
        raise

    return marc.rstrip()
