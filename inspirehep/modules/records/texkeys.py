# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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

"""Texkeys util functions."""

from __future__ import absolute_import, division, print_function

from datetime import date
from datetime import datetime
import logging
import random
import re
import string
import sys
import unicodedata
from unidecode import unidecode

from invenio_db import db
from invenio_pidstore.errors import PIDAlreadyExists, PIDDoesNotExistError
from invenio_pidstore.models import PersistentIdentifier, PIDStatus
from invenio_pidstore.providers.base import BaseProvider

from inspirehep.utils.date import extract_earliest_date

IS_PYTHON_3 = sys.version_info[0] == 3
LOGGER = logging.getLogger(__name__)


def generate_texkey(record):
    """Generate a texkey based on the data in the record.

    :param record: the record that needs the texkey
    :type record: dict

    :return: return the new texkey if it is
    able to produce it, otherwise empty string
    :rtype: string
    """
    new_texkey = ''
    first_part = first_part_generator(record)
    if first_part:
        new_texkey = '{}:{}{}'.format(
            first_part,
            second_part_generator(record),
            third_part_generator()
        )
    return new_texkey


def first_part_generator(record):
    """It generates the first part of the texkey.

    :param record: the record that needs the texkey
    :type record: dict

    :return: return the first part of the texkey
    if it is able to produce it, otherwise empty string
    :rtype: string
    """
    if 1 <= len(record.get('authors', [])) < 10:
        first_part = sanitize(record['authors'][0]['full_name'])
    elif record.get('collaborations', []):
        first_part = sanitize(record['collaborations'][0]['value'])
    elif record.get('corporate_author', []):
        first_part = sanitize(record['corporate_author'][0])
    elif 'proceedings' in record.get('document_type', []):
        first_part = 'proceedings'
    elif record.get('authors', []):
        first_part = sanitize(record['authors'][0]['full_name'])
    else:
        first_part = ''

    return first_part


def second_part_generator(record):
    """It generates the second part of the texkey.

    :param record: the record that needs the texkey
    :type record: dict

    :return: return the year of the record if it
    is able to extract it, otherwise the current year
    :rtype: string
    """
    def _get_year_from_record(record):
        earliest_date = extract_earliest_date(record)

        if earliest_date:
            return re.search(r'\d{4}', earliest_date).group(0)

        if record.created:
            return record.created.year

        return str(date.today().year)

    return _get_year_from_record(record)


def third_part_generator():
    """It generates the second part of the texkey.

    :param record: the record that needs the texkey
    :type record: dict

    :return: return the year of the record if it
    is able to extract it, otherwise the current year
    :rtype: string
    """
    random_sequence = get_three_random_letters()
    return random_sequence


def is_current_texkey_valid(record):
    """It checks if inside the record there is a valid texkey.

    :param record: the record that needs the texkey
    :type record: dict

    :return: return True if there is a valid texkey otherwise False
    :rtype: boolean
    """
    fixed_part = '{}:{}'.format(
        first_part_generator(record),
        second_part_generator(record),
    )

    previous_texkeys = record.get('texkeys', [''])
    return fixed_part in previous_texkeys[0]


def get_three_random_letters():
    """It generates a string composed by 3 random letters.

    :return: return a string of lenght 3
    :rtype: string
    """
    return ''.join(
        random.choice(
            string.ascii_lowercase
        ) for _ in range(3)
    )


def store_texkeys_pidstore(new_texkey, record, obj_uuid):
    """It stores the tekeys in the pidstore
    table if has not been used before.

    :param new_texkey: the texkey that has to be saved
    :type new_texkey: string

    :param record: the record related to the texkey
    :type new_texkey: string

    :return: return False if the key is already present,
    True if the key has been stored correctly
    :rtype: boolean
    """
    try:
        TexKeyIdProvider.create(
            'tex',
            obj_uuid,
            pid_value=new_texkey
        )
        return True
    except PIDAlreadyExists:
        return False


def sanitize(value):
    """It sanitizes a string.

    It converts the string in ASCII and it removes all the
    special unicode chars and it checks that the string
    is composed by all chars

    :param value: the string that has to be sanitized
    :type value: string

    :return: return the sanitized string
    :rtype: string
    """

    def _asciify(string):
        """Transliterate a string to ASCII."""
        if not IS_PYTHON_3 and not isinstance(string, unicode):
            string = unicode(string, 'utf8', errors='ignore')

        string = unidecode(unicodedata.normalize('NFKD', string))
        string = string.encode('ascii', 'ignore')
        string = string.decode('utf8')

        return string

    def _remove_bibtex_invalid_chars(value):
        return re.sub(
            r'[^-A-Za-z0-9.:/^_;&*<>?|!$+]',
            '',
            value
        )

    def _contains_a_letter(value):
        return re.search(
            r'[A-Za-z]',
            value
        )

    value = _asciify(value)
    try:
        value = value.split(',')[0]
    except KeyError:
        value = ''

    value = _remove_bibtex_invalid_chars(value)
    if len(value) == 0 or not _contains_a_letter(value):
        value = ''

    return value


class TexkeyMinterError(Exception):
    """Not able to produce a tekey identifier."""


class TexkeyMinterAlreadyValid(Exception):
    """The record contains already a valid key."""


def inspire_texkey_minter(obj_uuid, record):
    """Add to a record the texkey generated.

    if the texkey is already valid it does not add the texkey.
    if it is not able to generate the texkey it does not add the texkey.

    :param obj_uuid: the object uuid for a given record,
    necessary to store the pid record
    :type obj_uuid: string

    :param record: the record from which the texkey has to be added
    :type record: dict
    """
    if is_current_texkey_valid(record):
        raise TexkeyMinterAlreadyValid

    new_texkey = create_valid_texkey(record, obj_uuid)
    if not new_texkey:
        raise TexkeyMinterError

    return new_texkey


def create_valid_texkey(record, obj_uuid):
    """It creates a texkey.

    If the texkey cannot be created it returns None.
    If the texkey already exists it creates a new one until
    a correct one has been produced.

    :param obj_uuid: the object uuid for a given record,
    necessary to store the pid record
    :type obj_uuid: string

    :param record: the record from which the texkey has to be generated
    :type record: dict
    """
    for attempt in range(20):
        new_texkey = generate_texkey(record)

        if not new_texkey:
            return

        if store_texkeys_pidstore(new_texkey, record, obj_uuid):
            record.setdefault('texkeys', [])
            record['texkeys'].insert(0, new_texkey)
            return new_texkey

        LOGGER.debug(
            'Attempt number %d. The texkey produced is already present in the database.',
            attempt
        )
    return None


class TexKeyIdProvider(BaseProvider):
    """Record identifier provider."""

    pid_type = 'tex'
    """Type of persistent identifier."""

    pid_provider = None
    """Provider name.
    The provider name is not recorded in the PID since the provider does not
    provide any additional features besides creation of record ids.
    """

    default_status = PIDStatus.REGISTERED
    """Record IDs are by default registered immediately."""

    @classmethod
    def create(cls, object_type=None, object_uuid=None, **kwargs):
        """Create a new record identifier."""
        return super(
            TexKeyIdProvider, cls
        ).create(
            object_type=object_type, object_uuid=object_uuid, **kwargs
        )


def migrate_texkeys_from_legacy(obj_uuid, record):
    """Migrate old texkeys which come from the legacy

    :param obj_uuid: the object uuid for a given record,
    necessary to store the pid record
    :type obj_uuid: string

    :param record: the record where the old texkeys are stored
    :type record: dict
    """
    for texkey in record.get('texkeys', []):
        if not store_texkeys_pidstore(texkey, record, obj_uuid):
            LOGGER.debug(
                'The texkey %s is already present in the database.',
                texkey
            )
