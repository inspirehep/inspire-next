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

"""Test *helpers* (_method_name(foo, bar):) from logic.py"""

from __future__ import (
    absolute_import,
    division,
    print_function,
)

from inspirehep.modules.disambiguation.logic import (
    _check_if_claimed,
    _create_set_from_signature,
    _create_uuid_key_dictionary,
    _select_profile_base,
)


def test_check_if_claimed_method():
    """Check if signature is claimed and if is assigned to a profile."""
    signature_base = {
        'author_affiliation': 'MIT, Cambridge, CTP',
        'author_name': 'Wang, Yi-Nan',
        'publication_id': '5203f671-c549-46fd-999f-c13485244ca8',
        'signature_id': 'afa4af84-8eb2-418f-976e-0cb128e2cea9',
    }

    signature_claimed = signature_base.copy()
    signature_claimed['author_recid'] = '1'
    signature_claimed['author_claimed'] = True
    signature_claimed_result = (True, '1')

    signature_not_claimed = signature_base.copy()
    signature_not_claimed['author_recid'] = '1'
    signature_not_claimed['author_claimed'] = False
    signature_not_claimed_result = (False, '1')

    # Second element of the tuple must be a str type.
    signature_missing_claim_and_result_result = (False, "None")

    assert _check_if_claimed(signature_claimed) == signature_claimed_result
    assert _check_if_claimed(signature_not_claimed) == \
        signature_not_claimed_result
    assert _check_if_claimed(signature_base) == \
        signature_missing_claim_and_result_result


def test_create_set_from_signature_method():
    """Check if author's name and affiliation will be returned as set."""
    signature_base = {
        'author_name': 'Wang, Yi-Nan',
        'publication_id': '5203f671-c549-46fd-999f-c13485244ca8',
        'signature_id': 'afa4af84-8eb2-418f-976e-0cb128e2cea9',
    }

    signature_with_affiliation = signature_base.copy()
    signature_with_affiliation['author_affiliation'] = "MIT, Cambridge, CTP"
    signature_with_affiliation_result = {"Wang, Yi-Nan", "MIT, Cambridge, CTP"}

    signature_missing_affiliation_field_result = {"Wang, Yi-Nan"}

    assert _create_set_from_signature(signature_with_affiliation) == \
        signature_with_affiliation_result
    assert _create_set_from_signature(signature_base) == \
        signature_missing_affiliation_field_result


def test_create_uuid_key_dictionary_method():
    """Check creating dictionaries based on signatures' ids."""
    signatures = [{
        'author_affiliation': 'Hua-Zhong Normal U.',
        'author_claimed': False,
        'author_name': 'Wang, Yaping',
        'author_recid': False,
        'publication_id': '81aff169-c55e-4132-af77-8918e50c839b',
        'signature_id': 'b565863a-cfe3-4722-a64f-40d7c8b8f796'
    }, {
        'author_affiliation': 'Heidelberg U.',
        'author_claimed': False,
        'author_name': 'Wang, Yifei',
        'author_recid': False,
        'publication_id': '81aff169-c55e-4132-af77-8918e50c839b',
        'signature_id': 'f1222d01-a462-41d8-b502-28b18136215d'
    }]

    signatures_result = {
        'b565863a-cfe3-4722-a64f-40d7c8b8f796': {
            'author_affiliation': 'Hua-Zhong Normal U.',
            'author_claimed': False,
            'author_name': 'Wang, Yaping',
            'author_recid': False,
            'publication_id': '81aff169-c55e-4132-af77-8918e50c839b',
            'signature_id': 'b565863a-cfe3-4722-a64f-40d7c8b8f796'
        },
        'f1222d01-a462-41d8-b502-28b18136215d': {
            'author_affiliation': 'Heidelberg U.',
            'author_claimed': False,
            'author_name': 'Wang, Yifei',
            'author_recid': False,
            'publication_id': '81aff169-c55e-4132-af77-8918e50c839b',
            'signature_id': 'f1222d01-a462-41d8-b502-28b18136215d'
        }
    }

    assert _create_uuid_key_dictionary(signatures) == signatures_result


def test_select_profile_base_method():
    """Selection of the most representative signature from a given list."""
    signatures_with_claim = {
        'b565863a-cfe3-4722-a64f-40d7c8b8f796': {
            'author_affiliation': 'Hua-Zhong Normal U.',
            'author_claimed': True,
            'author_name': 'Wang, Yaping',
            'author_recid': '1',
            'publication_id': '81aff169-c55e-4132-af77-8918e50c839b',
            'signature_id': 'b565863a-cfe3-4722-a64f-40d7c8b8f796'
        },
        'e884de1f-c4cd-4535-aa59-929490a3b2a2': {
            'author_affiliation': 'WE DO NOT CARE',
            'author_claimed': False,
            'author_name': 'BECAUSE IT IS NOT CLAIMED',
            'author_recid': False,
            'publication_id': 'cf28affb-e52d-4da9-b8fb-84d1d6227909',
            'signature_id': 'e884de1f-c4cd-4535-aa59-929490a3b2a2'
        }
    }

    signatures_with_claim_uuids = [
        'e884de1f-c4cd-4535-aa59-929490a3b2a2',
        'b565863a-cfe3-4722-a64f-40d7c8b8f796'
    ]

    signatures_with_claim_result = "b565863a-cfe3-4722-a64f-40d7c8b8f796"

    signatures_select_the_best_one = {
        'b565863a-cfe3-4722-a64f-40d7c8b8f796': {
            'author_claimed': False,
            'author_name': 'John Smith',
            'author_recid': False,
            'publication_id': '81aff169-c55e-4132-af77-8918e50c839b',
            'signature_id': 'b565863a-cfe3-4722-a64f-40d7c8b8f796'
        },
        'e884de1f-c4cd-4535-aa59-929490a3b2a2': {
            'author_affiliation': 'MIT',
            'author_claimed': False,
            'author_name': 'Smith, J',
            'author_recid': False,
            'publication_id': 'cf28affb-e52d-4da9-b8fb-84d1d6227909',
            'signature_id': 'e884de1f-c4cd-4535-aa59-929490a3b2a2'
        },
        '78ca584b-41a1-43ab-aadf-0ea6f55a0bcb': {
            'author_affiliation': 'MIT',
            'author_claimed': False,
            'author_name': 'John Smith',
            'author_recid': False,
            'publication_id': '483ebd86-78e4-49bc-8c9e-02c4f856e5e3',
            'signature_id': '78ca584b-41a1-43ab-aadf-0ea6f55a0bcb'
        }
    }

    signatures_select_the_best_one_uuids = [
        'b565863a-cfe3-4722-a64f-40d7c8b8f796',
        'e884de1f-c4cd-4535-aa59-929490a3b2a2',
        '78ca584b-41a1-43ab-aadf-0ea6f55a0bcb'
    ]

    signatures_select_the_best_one_result = \
        "78ca584b-41a1-43ab-aadf-0ea6f55a0bcb"

    assert _select_profile_base(signatures_with_claim,
                                signatures_with_claim_uuids) == \
        signatures_with_claim_result

    assert _select_profile_base(signatures_select_the_best_one,
                                signatures_select_the_best_one_uuids) == \
        signatures_select_the_best_one_result
