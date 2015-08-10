#
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
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

from inspire.ext.formatter_jinja_filters.general import apply_template_on_array


def email_links(record):
    """
        returns array of links to record emails
    """
    return apply_template_on_array([email["value"] for email in
                                    record.get('_public_emails', [])],
                                   'format/record/field_templates/email.tpl')


def url_links(record):
    """
        returns array of links to record emails
    """
    return apply_template_on_array([url["value"] for url in
                                    record.get('urls', [])],
                                   'format/record/field_templates/link.tpl')


def institutes_links(record):
    """
        returns array of links to record institutes
    """
    return apply_template_on_array(record.get('institute', []),
                                   'format/record/field_templates/institute.tpl')


def author_profile(record):
    """
        returns array of links to record profiles of authores
    """
    return apply_template_on_array(record.get('profile', []),
                                   'format/record/field_templates/author_profile.tpl')


def words(value, limit, separator=' '):
    """Return first `limit` number of words ending by `separator`' '"""
    return separator.join(value.split(separator)[:limit])


def words_to_end(value, limit, separator=' '):
    """Return last `limit` number of words ending by `separator`' '"""
    return separator.join(value.split(separator)[limit:])


def is_list(value):
    """Checks if an object is a list"""
    if isinstance(value, list):
        return True

def remove_duplicates(value):
    """Removes duplicate objects from a list and returns the list"""
    seen = set()
    uniq = []
    for x in value:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    return uniq

def has_space(value):
    """Checks if a string contains space"""
    if ' ' in value:
        return True

def count_words(value):
    """Counts the amount of words in a string"""
    import re
    from string import punctuation
    r = re.compile(r'[{}]'.format(punctuation))
    new_strs = r.sub(' ', value)
    return len(new_strs.split())

def is_intbit_set(value):
    from intbitset import intbitset
    if isinstance(value, intbitset):
        value = value.tolist()
    return value

def remove_duplicates_from_dict(value):
    return [dict(t) for t in set([tuple(d.items()) for d in value])]

def get_filters():
    return {
        'email_links': email_links,
        'institute_links': institutes_links,
        'author_profile': author_profile,
        'url_links': url_links,
        'words': words,
        'words_to_end': words_to_end,
        'is_list': is_list,
        'remove_duplicates': remove_duplicates,
        'has_space': has_space,
        'count_words': count_words,
        'is_intbit_set': is_intbit_set,
        'remove_duplicates_from_dict': remove_duplicates_from_dict,
    }
