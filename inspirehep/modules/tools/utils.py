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

from __future__ import absolute_import, division, print_function

import re

import six
from nameparser import HumanName

from refextract.documents.pdf import replace_undesirable_characters
from refextract.documents.text import wash_line

# Differentiate authors from affiliations:
# authors have a number after name, affiliations lines start with a number
split_authors_affs_pattern = re.compile(r'(.*?\d)\n+(\d.*)', flags=re.DOTALL)
# Differentiate affiliations from one another, line break is required
split_affs_pattern = re.compile(r'(\d+\.?[\s\t]*.*)\n*', flags=re.UNICODE)


def authorlist(text):
    """Call the relevant formatter depending on the existence of affiliations.

    Input can be in two different formats:
        F. Lastname, F.M. Otherlastname
    or
        F. Lastname1, F.M. Otherlastname1,2
        1 CERN
        2 Otheraffiliation

    There should always be only one affiliation per line and the affiliation
    ids in author names should be separated with commas.
    """
    if not text:
        return ''
    if not isinstance(text, six.text_type):
        text = text.decode('utf-8')
    # Do some pre-cleaning of the input string
    text = text.replace('\r', '')  # Input from the form contains unwanted \r's
    text = text.replace(u'†', '')
    text = text.replace(u'∗', '')
    text = re.sub(r'(\n+)', r'\n', text)
    text = replace_undesirable_characters(text)
    text = wash_line(text)

    # Assume that if there are numbers in author name, they are affilation ids.
    # Also assume that if one author has an affiliation, everyone else has too.
    if re.search(r'([a-zA-Z_-]+[\n]*\d+)', text):
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

    if len(fname) == 1 and '.' not in fname:
        fname += '.'
    if len(mname) == 1 and '.' not in mname:
        mname += '.'

    return u'{}{}{}'.format(
        lname,
        ', ' + fname if fname else '',
        ' ' + mname if mname else ''
    )


def authorlist_without_affiliations(text):
    """Return a MARC format string of authors without affiliations."""
    authors = text.replace(' and ', ', ').split(', ')
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
                r'(.+?)(\d+[\,\d]*)', author, flags=re.UNICODE
            ).groups()
        except AttributeError:
            raise
        fullname = format_name(name)
        aff_ids = [aff for aff in affs.split(',') if aff.isdigit()]

        return fullname, aff_ids

    def create_new_marcline(author, affiliations, first_author=False):
        """Get MARC line of the format '100__ $$aDurães, F.$$vCERN'."""
        try:
            fullname, aff_ids = parse_author_string(author)
        except AttributeError:
            raise AttributeError(
                'Cannot split affiliation IDs from author name. This author '
                'might not have an affiliation at all', author
            )
        try:
            affstring = ' '.join(
                [u'$$v{}'.format(affiliations[aff_id]) for aff_id in aff_ids]
            )
        except KeyError:
            raise KeyError(
                'There might be multiple affiliations per line or '
                'affiliation IDs might not be separated with commas or '
                'the affiliation is missing. '
                'Problematic author and affiliations: ', author, aff_ids,
                affiliations
            )

        if first_author:
            marcfield = '100'
        else:
            marcfield = '700'

        return u'{}__ $$a{}{}\n'.format(marcfield, fullname, affstring)

    # Try to work with badly formatted input
    # There should be commas between different affiliation ids in author
    # names and there should be only one affiliation name per line.
    split_auths_and_affs = split_authors_affs_pattern.search(text)
    if not split_auths_and_affs:
        raise AttributeError('Could not find affiliations')
    authors_raw = split_auths_and_affs.group(1)
    # ensure comma between affid and next author name:
    authors_raw = re.sub(r'(\d+)[\n\s](\D)', r'\1, \2', authors_raw)
    authors_raw = authors_raw.replace('\n', '')
    # ensure no comma between author name and its affids
    authors_raw = re.sub(r'(\D)\,[\n\s]*(\d)', r'\1\2', authors_raw)
    # ensure space between comma and next author name:
    authors_raw = re.sub(r'(\d+)\,(\S\D)', r'\1, \2', authors_raw)
    # ensure no spaces between affids of an author
    authors_raw = re.sub(r'(\d+)\,\s(\d+)', r'\1,\2', authors_raw)

    authors = authors_raw.replace(' and ', ', ').split(', ')

    # Extract affiliations:
    affs_raw = split_auths_and_affs.group(2)
    affs_list = split_affs_pattern.findall(affs_raw)
    affs_list = [aff.replace('\n', ' ').strip() for aff in affs_list]
    affiliations = {}
    for aff in affs_list:
        try:
            # Note that affiliation may contain numbers
            aff_id, aff_name = re.search(r'^(\d+)\.?\s?(.*)$', aff).groups()
            affiliations[aff_id] = aff_name
        except (ValueError, AttributeError):
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
