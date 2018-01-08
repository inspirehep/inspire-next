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

"""Helper functions for authors."""

from __future__ import absolute_import, division, print_function

import re
import copy
import datetime

import numpy as np
from flask import url_for
from beard.utils.strings import asciify
from beard.clustering import block_phonetic
from sqlalchemy.orm.exc import NoResultFound

from invenio_accounts.models import User
from invenio_oauthclient.models import UserIdentity

from inspire_dojson.utils import strip_empty_values
from inspire_schemas.api import validate
from inspirehep.modules.forms.utils import filter_empty_elements
from .dojson.model import updateform


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


def phonetic_blocks(full_names, phonetic_algorithm='nysiis'):
    """Create a dictionary of phonetic blocks for a given list of names."""

    # The method requires a list of dictionaries with full_name as keys.
    full_names_formatted = [
        {"author_name": i} for i in full_names]

    # Create a list of phonetic blocks.
    phonetic_blocks = list(
        block_phonetic(np.array(
            full_names_formatted,
            dtype=np.object).reshape(-1, 1),
            threshold=0,
            phonetic_algorithm=phonetic_algorithm
        )
    )

    return dict(zip(full_names, phonetic_blocks))


def formdata_to_model(formdata, id_workflow, id_user, is_update=False):
    """Generate the record model dict and extra_data dict from the form data.

    Returns:
        tuple(dict, dict): tuple containing the dict representaion of a record
            and the extra_data to create a new workflow.
    """
    form_fields = copy.deepcopy(formdata)
    extra_data = {}

    filter_empty_elements(
        form_fields,
        ['institution_history', 'advisors',
         'websites', 'experiments']
    )
    data = updateform.do(form_fields)

    data['_collections'] = ['Authors']

    if '$schema' in data and not data['$schema'].startswith('http'):
        data['$schema'] = url_for(
            'invenio_jsonschemas.get_schema',
            schema_path="records/{0}".format(data['$schema'])
        )

    author_name = ''

    if 'family_name' in form_fields and form_fields['family_name']:
        author_name = form_fields['family_name'].strip() + ', '
    if 'given_names' in form_fields and form_fields['given_names']:
        author_name += form_fields['given_names']

    if author_name:
        data.get('name', {})['value'] = author_name

    if 'extra_comments' in form_fields and form_fields['extra_comments']:
        data.setdefault('_private_notes', []).append({
            'source': 'submitter',
            'value': form_fields['extra_comments']
        })

    data['stub'] = False

    # ==========
    # Submitter Info
    # ==========
    try:
        user_email = User.query.get(id_user).email
    except AttributeError:
        user_email = ''
    try:
        orcid = UserIdentity.query.filter_by(
            id_user=id_user,
            method='orcid'
        ).one().id
    except NoResultFound:
        orcid = ''
    data['acquisition_source'] = dict(
        email=user_email,
        datetime=datetime.datetime.utcnow().isoformat(),
        method="submitter",
        orcid=orcid,
        submission_number=str(id_workflow),
        internal_uid=int(id_user),
    )

    data = strip_empty_values(data)

    validate(data, 'authors')

    if is_update is not None:
        extra_data['is-update'] = is_update

    return data, extra_data
