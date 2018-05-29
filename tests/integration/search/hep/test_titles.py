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

from __future__ import absolute_import, division, print_function

import json

from test_utils import parametrize


FIXTURES_FILE = 'hep_titles.xml.gz'


def _query_and_retrieve_control_numbers(client, query_string):
    response = client.get(
        '/literature/?q=' + query_string,
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)
    return set([recid for recid in response_json['hits']['recids']])


@parametrize(
    {
        'f t N-body and t separable': {
            'query_str': 'f t N-body and t separable', 'expected_recids': {
                # "The Relativistic N body problem in a separable two-body basis".
                534466,
                # 577837 title: "Reliability of the dark matter clustering in cosmological n-body simulation on scales
                # below the mean separation length of particles".
                # 313341 title: Exact n-d scattering calculation with a separable expansion of the two-body t matrix
                # i.e. must not be there.
            }
        },
        # TODO
        # 't n body (should return both "n body" and "n-body")': {
        #     'query_str': 't n body', 'expected_recids': {534466, 577837}
        # },
        't n-body two': {
            'query_str': 't n-body two', 'expected_recids': {534466}
        },
        't n-body two-body': {
            'query_str': 't n-body two-body', 'expected_recids': {534466}
        },
        'Find T g-2': {
            'query_str': 'Find T g-2', 'expected_recids': {
                627066,  # g-2

                # FIXME:
                # 1337596,  g - 2: Tricky case, as "-" token is understood as "not", and along with implicit and this
                # gets recognized as
                # AndOp(KeywordOp(Keyword('title'), Value('g')), NotOp(KeywordOp(Keyword('title'), Value('2')))).
                # The restructuring visitor should be helpful for this.

                # 599587 title: G(2) quivers, must not be there due to g-2 and G(2) being completely different concepts.
            }
        },
        't SU(2)': {
            'query_str': 't SU(2)', 'expected_recids': {
                50248,  # SU(2) --> SU(3) --> SU(6)
                # 1418375 title: SU(2|1) Supersymmetric Mechanics, must not match.
                # 650082 title: Ferromagnetic SU(2)-ground state, must not match.
            }
        },
        'find t A First Course in String Theory': {
            'query_str': 'find t A First Course in String Theory', 'expected_recids': {660149}
        },
        # TODO
        # 'find t /wigner function/': {
        #     'query_str': 'find t /wigner function/', 'expected_recids': {
        #         # "Wigner functions on non-standard symplectic vector spaces".
        #         1648003,
        #         # "Complete and Consistent Chiral Transport from Wigner Function Formalism".
        #         1647579,
        #         # 1635924 title: "Wigner Distributions Using Light-Front Wave Functions", must not match.
        #     }
        # }
    }
)
def test_titles_search(search_api_client, query_str, expected_recids):
    assert _query_and_retrieve_control_numbers(search_api_client, query_str) == expected_recids,\
        "Query was [" + query_str + "]"
