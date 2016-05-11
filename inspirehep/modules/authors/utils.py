# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""Helper functions for authors."""

import re

try:
    from beard.utils.strings import asciify
except ImportError:
    import sys
    import unicodedata
    from functools import wraps

    from unidecode import unidecode

    IS_PYTHON_3 = sys.version_info[0] == 3

    def memoize(func):
        """Memoization function."""
        cache = {}

        @wraps(func)
        def wrap(*args, **kwargs):

            frozen = frozenset(kwargs.items())
            if (args, frozen) not in cache:
                cache[(args, frozen)] = func(*args, **kwargs)
            return cache[(args, frozen)]

        return wrap

    @memoize
    def asciify(string):
        """Transliterate a string to ASCII."""
        if not IS_PYTHON_3 and not isinstance(string, unicode):
            string = unicode(string, "utf8", errors="ignore")

        string = unidecode(unicodedata.normalize("NFKD", string))
        string = string.encode("ascii", "ignore")
        string = string.decode("utf8")

        return string


_bai_parentheses_cleaner = \
    re.compile(r"(\([^)]*\))|(\[[^\]]*\])|(\{[^\}]*\})", re.UNICODE)
_bai_last_name_separator = re.compile(r"[,;]+", re.UNICODE)
_bai_names_separator = re.compile("[,;.=\-\s]+", re.UNICODE)
_bai_special_char_mapping = {'ß': 'ss', 'ä': 'ae', 'ö': 'oe', 'ü': 'ue'}
_bai_nonletters = re.compile(r"[^\w\s]|\d", re.UNICODE)
_bai_spaces = re.compile(r"\s+", re.UNICODE)
_bai_particles = ["da", "de", "del", "den", "der",
                  "du", "van", "von", "het", "y"]
split_on_re = re.compile('[\.\s-]')
single_initial_re = re.compile('^\w\.$')


def _nonempty(words):
    words = [w.strip() for w in words]
    words = [w for w in words if len(w) >= 1]
    return words


def bai(name):
    # Remove content in parentheses
    name = _bai_parentheses_cleaner.sub("", name)

    # Get last name and initials
    names = _bai_last_name_separator.split(name, maxsplit=1)
    names = _nonempty(names)

    if len(names) == 1:
        names = _bai_spaces.split(name, maxsplit=1)
        names = _nonempty(names)

    if len(names) == 0:
        return ""

    elif len(names) == 2:
        last_name = names[0]
        initials = [w[0].upper()
                    for w in _bai_names_separator.split(names[1]) if w]

    else:
        last_name = names[0]
        initials = []

    # Asciify
    for char, replacement in _bai_special_char_mapping.items():
        last_name = last_name.replace(char, replacement)
        initials = [i.replace(char, replacement) for i in initials]

    last_name = asciify(last_name)
    initials = _nonempty([asciify(i) for i in initials])

    # Capitalize words in last name
    words = _bai_names_separator.split(last_name)
    words = _nonempty(words)

    for i, w in enumerate(words):
        if w.lower() in _bai_particles and i < len(words) - 1:
            words[i] = w.lower()
        elif (all([c.isupper() or c == "'" for c in w]) or
              all([c.islower() or c == "'" for c in w])):
            words[i] = w.title()
        else:
            words[i] = w

    bai = "%s %s" % (" ".join(initials), " ".join(words))

    # Keep letters and spaces
    bai = _bai_nonletters.sub("", bai)
    bai = bai.strip()

    # Replace all spaces with .
    bai = _bai_spaces.sub(".", bai)

    return bai


def scan_author_string_for_phrases(s):
    """Scan a name string and output an object representing its structure.

       Sample output for the name 'Jingleheimer Schmitt, John Jacob, XVI.' is:
       {
        'TOKEN_TAG_LIST' : ['lastnames', 'nonlastnames', 'titles', 'raw'],
        'lastnames'      : ['Jingleheimer', 'Schmitt'],
        'nonlastnames'   : ['John', 'Jacob'],
        'titles'         : ['XVI.'],
        'raw'            : 'Jingleheimer Schmitt, John Jacob, XVI.'
        }

    :param s: the input to be lexically tagged
    :type s: string
    :returns: dict of lexically tagged input items.
    :rtype: dict
    """

    retval = {
        'TOKEN_TAG_LIST': [
            'lastnames',
            'nonlastnames',
            'titles',
            'raw'],
        'lastnames': [],
        'nonlastnames': [],
        'titles': [],
        'raw': s}
    l = s.split(',')
    if len(l) < 2:
        # No commas means a simple name
        new = s.strip()
        new = s.split(' ')
        if len(new) == 1:
            retval['lastnames'] = new        # rare single-name case
        else:
            retval['lastnames'] = new[-1:]
            retval['nonlastnames'] = new[:-1]
            for tag in ['lastnames', 'nonlastnames']:
                retval[tag] = [x.strip() for x in retval[tag]]
                retval[tag] = [re.split(split_on_re, x)
                               for x in retval[tag]]
                # flatten sublists
                retval[tag] = [item for sublist in retval[tag]
                               for item in sublist]
                retval[tag] = [x for x in retval[tag] if x != '']
    else:
        # Handle lastname-first multiple-names case
        retval['titles'] = l[2:]             # no titles? no problem
        retval['nonlastnames'] = l[1]
        retval['lastnames'] = l[0]
        for tag in ['lastnames', 'nonlastnames']:
            retval[tag] = retval[tag].strip()
            retval[tag] = re.split(split_on_re, retval[tag])
            # filter empty strings
            retval[tag] = [x for x in retval[tag] if x != '']
        retval['titles'] = [x.strip() for x in retval['titles'] if x != '']

    return retval


def parse_scanned_author_for_phrases(scanned):
    """Return all the indexable variations for a tagged token dictionary.
    Does this via the combinatoric expansion of the following rules:
    - Expands first names as name, first initial with period, first initial
        without period.
    - Expands compound last names as each of their non-stopword subparts.
    - Titles are treated literally, but applied serially.
    Please note that titles will be applied to complete last names only.
    So for example, if there is a compound last name of the form,
    "Ibanez y Gracia", with the title, "(ed.)", then only the combination
    of those two strings will do, not "Ibanez" and not "Gracia".

    :param scanned: lexically tagged input items in the form of the output
        from scan()
    :type scanned: dict
    :returns: combinatorically expanded list of strings for indexing
    :rtype: list of string
    """
    def _fully_expanded_last_name(first, lastlist, title=None):
        """Return a list of all of the first / last / title combinations.

        :param first: one possible non-last name
        :type first: string
        :param lastlist: the strings of the tokens in the (possibly compound) last name
        :type lastlist: list of string
        :param title: one possible title
        :type title: string
        """
        lastname_stopwords = set(['y', 'of', 'and', 'de'])
        retval = []
        title_word = ''
        if title is not None:
            title_word = ', ' + title

        last = ' '.join(lastlist)
        retval.append(first + ' ' + last + title_word)
        retval.append(last + ', ' + first + title_word)
        retval.append(last + ' ' + first + title_word)
        for last in lastlist:
            if last in lastname_stopwords:
                continue
            retval.append(first + ' ' + last + title_word)
            retval.append(last + ', ' + first + title_word)
        retval += lastlist
        return retval

    last_parts = scanned['lastnames']
    first_parts = scanned['nonlastnames']
    titles = scanned['titles']

    if len(first_parts) == 0:                       # rare single-name case
        return scanned['lastnames']

    expanded = []
    for exp in expand_nonlastnames(first_parts):
        expanded.extend(_fully_expanded_last_name(exp, last_parts, None))
        for title in titles:
            # Drop titles which are parenthesized.  This eliminates (ed.) from the index, but
            # leaves XI, for example.  This gets rid of the surprising behavior that searching
            # for 'author:ed' retrieves people who have been editors, but whose names aren't
            # Ed.
            # TODO: Make editorship and other special statuses a MARC
            # field.
            if title.find('(') != -1:
                continue
            # XXX: remember to document that titles can only be applied to
            # complete last names
            expanded.extend(_fully_expanded_last_name(
                exp, [' '.join(last_parts)], title))

    return sorted(list(set(expanded)))


def expand_nonlastnames(namelist):
    """Generate every expansion of a series of human non-last names.

    Example:
    "Michael Edward" -> "Michael Edward", "Michael E.", "Michael E", "M. Edward", "M Edward",
                        "M. E.", "M. E", "M E.", "M E", "M.E."
                ...but never:
                "ME"

    :param namelist: a collection of names
    :type namelist: list of string
    :returns: a greatly expanded collection of names
    :rtype: list of string
    """

    def _expand_name(name):
        """Lists [name, initial, empty]"""
        if name is None:
            return []
        return [name, name[0]]

    def _pair_items(head, tail):
        """Lists every combination of head with each and all of tail"""
        if len(tail) == 0:
            return [head]
        l = []
        l.extend([head + ' ' + tail[0]])
        l.extend(_pair_items(head, tail[1:]))
        return l

    def _collect(head, tail):
        """Brings together combinations of things"""

        def _cons(a, l):
            l2 = l[:]
            l2.insert(0, a)
            return l2

        if len(tail) == 0:
            return [head]
        l = []
        l.extend(_pair_items(head, _expand_name(tail[0])))
        l.extend([' '.join(_cons(head, tail)).strip()])
        l.extend(_collect(head, tail[1:]))
        return l

    def _expand_contract(namelist):
        """Runs collect with every head in namelist and its tail"""
        val = []
        for i in range(len(namelist)):
            name = namelist[i]
            for expansion in _expand_name(name):
                val.extend(_collect(expansion, namelist[i + 1:]))
        return val

    def _add_squashed(namelist):
        """Finds cases like 'M. E.' and adds 'M.E.'"""
        val = namelist

        def __check_parts(parts):
            if len(parts) < 2:
                return False
            for part in parts:
                if not single_initial_re.match(part):
                    return False
            return True

        for name in namelist:
            parts = name.split(' ')
            if not __check_parts(parts):
                continue
            val.extend([''.join(parts)])

        return val

    return _add_squashed(_expand_contract(namelist))


def author_tokenize(phrase):
    """Return all possible variatons of a name"""
    return parse_scanned_author_for_phrases(
        scan_author_string_for_phrases(phrase))
