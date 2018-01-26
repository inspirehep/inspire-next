# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.


"""Functions to parse an authorlist."""

from __future__ import absolute_import, division, print_function

import re
import six

re_emptyline = re.compile(r'\n\s*\n', re.UNICODE)
re_hyphens = re.compile(
    r'(\\255|\u02D7|\u0335|\u0336|\u2212|\u2013|\u002D|\uFE63|\uFF0D)', re.UNICODE)
re_multiple_space = re.compile(r'\s{2,}', re.UNICODE)
re_potential_key = re.compile(r"^(?:\d|[^\w.'-])+$", re.UNICODE)
re_trailing_nonword = re.compile(r"((?:\d|[^\w,.'-])+ )", re.UNICODE)
re_symbols = re.compile(r'[^\w ]', re.UNICODE)


def split_id(word):
    """
    Separate potential aff-ids .
    E.g.: '*12%$' -> ['*', '12' '%', '$']
    """

    aff_ids = []

    symbols = re_symbols.findall(word)
    if symbols:
        aff_ids += symbols
        for rest in re_symbols.split(word):
            if rest:
                aff_ids.append(rest)
    else:
        aff_ids.append(word)
    return aff_ids


def parse_authors(text, affiliations):
    """
    Parse author names and convert to Lastname, Firstnames.
    Can be separated by ',', newline or affiliation tag.
    Returns:
    List of tuples: (author_fullname, [author_affiliations])
    List of strings: warnings
    """
    import copy

    authors = []
    warnings = []

    text = text.replace(',', ' , ')
    text = text.replace('\n', ' , ')
    text = text.replace(' and ', ' , ') + ' '
    text = re_trailing_nonword.sub(r' \1', text)
    text = re_multiple_space.sub(' ', text)

    aff_keys = affiliations.keys()
    unused_aff_keys = copy.deepcopy(aff_keys)
    key_type = ''
    if aff_keys:
        if aff_keys[0].isalpha():
            key_type = 'alpha'
        elif aff_keys[0].isdigit():
            key_type = 'digit'
        else:
            key_type = 'symbol'
            warnings.append('CAUTION! Using symbols (# and stuff) as aff-IDs.')
    else:
        warnings.append('Found no affiliations (empty line needed)')

    author_names = []
    author_affs = []
    fullname = ''
    list_of_words = text.split(' ')
    for nw, word in enumerate(list_of_words):
        if word in aff_keys or word == ',' or re_potential_key.search(word):
            # author name stops here, add affiliations
            if author_names:
                fullname = ' '.join(author_names)
                if len(author_names) == 1:
                    warnings.append('Author without firstname: %s' % fullname)
                author_names = []
            if word in aff_keys:
                author_affs.append(affiliations[word])
                if word in unused_aff_keys:
                    unused_aff_keys.remove(word)
            elif not word == ',':
                # something left over or not separated
                for aff_key in split_id(word):
                    if aff_key in aff_keys:
                        author_affs.append(affiliations[aff_key])
                        if aff_key in unused_aff_keys:
                            unused_aff_keys.remove(aff_key)
                    else:
                        warnings.append(
                            'Unresolved aff-ID or stray footnote symbol. '
                            'Problematic author and aff-id: %s %s' %
                            (fullname, aff_key)
                        )
        else:
            # (part of) (next) author name, process previous author
            if key_type == 'alpha' and word.islower() and word.isalpha():
                three_words = \
                    list_of_words[max(nw-2, 0):min(nw+3, len(list_of_words))-1]
                warnings.append(
                    'Is this part of a name or missing aff-id? "%s" in %s' %
                    (word, ' '.join(three_words))
                )
            if fullname:
                if affiliations and not author_affs:
                    # there should be affiliations
                    warnings.append(
                       'Author without affiliation-id. '
                       'Problematic author: %s' % fullname
                    )

                authors.append((fullname, author_affs))
                author_affs = []
                fullname = ''
            if word:
                author_names.append(word)

    if author_names:
        fullname = ' '.join(author_names)
        if len(author_names) == 1:
            warnings.append('Author without firstname: %s' % fullname)
        author_affs = []
    if fullname:
        authors.append((fullname, author_affs))

    if unused_aff_keys:
        warnings.append('Unused affiliation-IDs: %s' % unused_aff_keys)

    return authors, warnings


def determine_aff_type_character(char_list):
    """
    Guess whether affiliation are by number, letter or symbols (e.g. dagger).
    Numbers and letters should not be mixed.
    """

    aff_type = None
    for char in char_list:
        if aff_type:
            if aff_type == 'alpha':
                if not char.isalpha():
                    return None
            elif aff_type == 'digit':
                if not char.isdigit():
                    return None
        else:
            if char.isalpha():
                aff_type = 'alpha'
            elif char.isdigit():
                aff_type = 'digit'
            else:
                aff_type = 'symbol'
                break
    return aff_type


def determine_aff_type(text):
    """
    Guess format for affiliations.
    Return corresponding search pattern.
    """

    line_pattern_single = {'alpha': re.compile(r'^([a-z]+)\.*$', re.UNICODE),
                           'digit': re.compile(r'^(\d+)\.*$', re.UNICODE),
                           'symbol': re.compile(r'^(.)\.*$', re.UNICODE)}

    line_pattern_line = {'alpha': re.compile(r'^([a-z]+)[ .]+(.*)', re.UNICODE),
                         'digit': re.compile(r'^(\d+)[ .]*(.*)', re.UNICODE),
                         'symbol': re.compile(r'^(.)[ .]+(.*)', re.UNICODE)}

    single_char = []
    first_char = []
    for line in text.split('\n'):
        line = line.strip(' .')
        if len(line) == 1:
            single_char.append(line)
        elif line:
            first_char.append(line[0])

    if single_char:
        aff_type = determine_aff_type_character(single_char)
        if aff_type:
            aff_pattern = line_pattern_single[aff_type]
        else:
            raise ValueError('Cannot identify type of affiliation, '
                             'found IDs: %s' % single_char)
    else:
        aff_type = determine_aff_type_character(first_char)
        if aff_type:
            aff_pattern = line_pattern_line[aff_type]
        else:
            raise ValueError('Cannot identify type of affiliations, '
                             'found IDs: %s' % first_char)

    return aff_pattern


def parse_affiliations(text):
    """
    Determine how affiliations are formatted.
    Return hash of id:affiliation

    Allowed formats:
    don't mix letters and numbers, lower-case letters only

    1
    CERN, Switzerland
    2
    DESY,
    Germany


    1 CERN, Switzerland
    2DESY, Germany

    a  CERN, Switzerland
    bb DESY, Germany

    *
    CERN, Switzerland
    #
    DESY, Germany
    """

    affiliations = {}
    aff_pattern = determine_aff_type(text)

    aff_id = None
    this_aff = []
    for line in text.split('\n'):
        line = line.strip()
        get_affiliation = aff_pattern.search(line)
        if get_affiliation:
            if len(get_affiliation.groups()) == 2:
                affiliations[get_affiliation.group(1)] = \
                    get_affiliation.group(2).strip()
            else:
                if aff_id and this_aff:
                    affiliations[aff_id] = ' '.join(this_aff).strip()
                    aff_id = None
                    this_aff = []
                aff_id = get_affiliation.group(1)
        elif aff_id:
            this_aff.append(line)
        elif line:
            raise ValueError('Something is wrong with the affiliation list')
    if aff_id and this_aff:
        affiliations[aff_id] = ' '.join(this_aff).strip()

    return affiliations


def create_authors(text):
    """
    Split text in (useful) blocks, sepatated by empty lines.
    1 block: no affiliations
    2 blocks: authors and affiliations
    more blocks: authors grouped by affiliation (not implemented yet)

    Returns:
        dict: with two keys: ``authors`` of the form ``(author_fullname,
        [author_affiliations])`` and ``warnings`` which is a list of strings.
    """

    if not text:
        return {}

    if not isinstance(text, six.text_type):
        text = text.decode('utf-8')
    text = text.replace('\r', '')  # Input from the form contains unwanted \r's
    text = re_hyphens.sub('-', text)

    empty_blocks = []
    text_blocks = re_emptyline.split(text)
    for num, block in enumerate(text_blocks):
        if not re.search(r'\w', block):
            empty_blocks.append(num)
    empty_blocks.reverse()
    for num in empty_blocks:
        text_blocks.pop(num)

    if len(text_blocks) == 0:
        authors, warnings = [], []
    elif len(text_blocks) == 1:
        authors, warnings = parse_authors(text_blocks[0], {})
    elif len(text_blocks) == 2:
        affiliations = parse_affiliations(text_blocks[1])
        authors, warnings = parse_authors(text_blocks[0], affiliations)
    else:
        # authors = parse_blocks(text_blocks)
        raise ValueError('Authors grouped by affiliation? - Comming soon.'
                         'Or too many empty lines.')

    if warnings:
        return {'authors': authors, 'warnings': warnings}
    else:
        return {'authors': authors}
