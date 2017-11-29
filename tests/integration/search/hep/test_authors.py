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


FIXTURES_FILE = 'hep_authors.xml.gz'


def _query_and_retrieve_control_numbers(client, query_string):
    response = client.get(
        '/literature/?q=a ' + query_string,
        headers={'Accept': 'application/vnd+inspire.ids+json'}
    )

    assert response.status_code == 200

    response_json = json.loads(response.data)
    return set([recid for recid in response_json['hits']['recids']])


@parametrize(
    {
        # One lastname, one non lastname
        # All query variations for one firstname - one lastname query.
        'Lastname, Firstname': {'query_str': 'Mele, Salvatore', 'expected_recids': {1497857, 1507918, 578814}},
        'Firstname Lastname': {'query_str': 'Salvatore Mele', 'expected_recids': {1497857, 1507918, 578814}},
        'Lastname Firstname': {'query_str': 'Mele Salvatore', 'expected_recids': {1497857, 1507918, 578814}},

        # Unicode lastname search (and equivalence with its transliterated version)
        'uLastname, Firstname':
            {'query_str': u'Müller, Thomas', 'expected_recids': {1633763, 1618250}},
        'Firstname uLastname':
            {'query_str': u'Thomas Müller', 'expected_recids': {1633763, 1618250}},
        'uLastname Firstname':
            {'query_str': u'Müller Thomas', 'expected_recids': {1633763, 1618250}},

        'Lastname, Firstname (equiv. with unicode)':
            {'query_str': 'Muller, Thomas', 'expected_recids': {1633763, 1618250}},
        'Firstname Lastname (equiv. with unicode)':
            {'query_str': 'Thomas Muller', 'expected_recids': {1633763, 1618250}},
        'Lastname Firstname (equiv. with unicode)':
            {'query_str': 'Muller Thomas', 'expected_recids': {1633763, 1618250}},

        # Only lastname search
        'Lastname': {'query_str': 'mele', 'expected_recids': {1497857, 1507918, 578814, 337321, 832224}},
        'uLastname': {'query_str': u'müller', 'expected_recids': {1633763, 1618250, 850589}},
        'transliterate(lastname)': {'query_str': 'muller', 'expected_recids': {1633763, 1618250, 850589}},


        # All query variations for single lastname and initial(firstname)
        'Lastname, initial(Firstname)': {
            'query_str': 'Mele, S', 'expected_recids': {1497857, 1507918, 578814, 832224}
        },
        'Lastname, initial(Firstname).': {
            'query_str': 'Mele, S.', 'expected_recids': {1497857, 1507918, 578814, 832224}
        },
        'initial(Firstname) Lastname': {
            'query_str': 'S Mele', 'expected_recids': {1497857, 1507918, 578814, 832224}
        },
        'initial(Firstname). Lastname': {
            'query_str': 'S. Mele', 'expected_recids': {1497857, 1507918, 578814, 832224}
        },

        # All query variations with single lastname and initial(firstname) in unicode form and its transliterated
        # version
        'uLastname, initial(Firstname)': {
            'query_str': u'Müller, T', 'expected_recids': {1633763, 1618250}
        },
        'uLastname, initial(Firstname).': {
            'query_str': u'Müller, T.', 'expected_recids': {1633763, 1618250}
        },
        'initial(Firstname) uLastname': {
            'query_str': u'T Müller', 'expected_recids': {1633763, 1618250}
        },
        'initial(Firstname). uLastname': {
            'query_str': u'T. Müller', 'expected_recids': {1633763, 1618250}
        },
        'transliterate(Lastname), initial(Firstname)': {
            'query_str': 'Muller, T', 'expected_recids': {1633763, 1618250}
        },
        'transliterate(Lastname), initial(Firstname).': {
            'query_str': 'Muller, T.', 'expected_recids': {1633763, 1618250}
        },
        'initial(Firstname) transliterate(Lastname)': {
            'query_str': 'T Muller', 'expected_recids': {1633763, 1618250}
        },
        'initial(Firstname). transliterate(Lastname)': {
            'query_str': 'T. Muller', 'expected_recids': {1633763, 1618250}
        },

        # TODO we can improve and not match the latter one (contains Garcia A)
        # 'Garcia, Alfonso': {
        #     'query_str': 'Garcia, Alfonso', 'expected_recids': {1633763, 1618250}
        # },

        # Multiple lastnames
        # Queries with all lastnames
        'all(Lastnames), Firstname': {
            'query_str': 'Garcia-Sciveres, Maurice', 'expected_recids': {1601506, 1508016, 1510725}
        },
        'Firstname all(Lastnames)': {
            'query_str': 'Maurice Garcia-Sciveres', 'expected_recids': {1601506, 1508016, 1510725}
        },
        'all(Lastnames) Firstname': {
            'query_str': 'Garcia-Sciveres Maurice', 'expected_recids': {1601506, 1508016, 1510725}
        },

        # Single Lastname queries
        'first(Lastname), Firstname': {
            'query_str': 'Garcia, Maurice', 'expected_recids': {1601506, 1508016, 1510725}
        },
        'Firstname first(Lastname)': {
            'query_str': 'Maurice Garcia', 'expected_recids': {1601506, 1508016, 1510725}
        },
        'first(Lastname) Firstname': {
            'query_str': 'Garcia Maurice', 'expected_recids': {1601506, 1508016, 1510725}
        },

        # TODO currently it does not match (but when we add the 2nd lastname variations it will.
        # The latter record below matches as it contains an author called `Vizan Garcia, Jesus Manuel` (so it has both
        # `Garcia` and `M`). Additionally, the name variations of this author contain the entry `Garcia, M` which is
        # needed to be able to support searching with 2nd lastname of authors.

        'first(Lastname), initial(Firstname)': {
            'query_str': 'Garcia, M', 'expected_recids': {1601506, 1508016, 1510725}
        },
        'initial(Firstname) first(Lastname)': {
            'query_str': 'M Garcia', 'expected_recids': {1601506, 1508016, 1510725}
        },
        'first(Lastname) initial(Firstname)': {
            'query_str': 'Garcia M', 'expected_recids': {1601506, 1508016, 1510725}
        },

        # In order to make the below queries work, I've added name variations which contain not only the first
        # lastname, but the others, as well.
        # This resulted in records where the 2nd lastname was "Garcia" and a firstname was "Manuel", thus a "Garcia, M"
        # variation was generated, which entailed one more record getting matched above.
        # The explanation for this is above.
        # So, the solution was to add min_score = 0.1 in the queries. We need to investigate whether this is ok.
        #
        # 'second(Lastname), Firstname': {
        #     'query_str': 'Sciveres, Maurice', 'expected_recids': {1601506, 1508016, 1510725}
        # },
        # 'Firstname second(Lastname)': {
        #     'query_str': 'Maurice Sciveres', 'expected_recids': {1601506, 1508016, 1510725}
        # },
        # 'second(Lastname) Firstname': {
        #     'query_str': 'Sciveres Maurice', 'expected_recids': {1601506, 1508016, 1510725}
        # },
        #
        # 'second(Lastname), initial(Firstname)': {
        #     'query_str': 'Sciveres, M', 'expected_recids': {1601506, 1508016, 1510725}
        # },
        # 'initial(Firstname) second(Lastname)': {
        #     'query_str': 'M Sciveres', 'expected_recids': {1601506, 1508016, 1510725}
        # },
        # 'second(Lastname) initial(Firstname)': {
        #     'query_str': 'Sciveres M', 'expected_recids': {1601506, 1508016, 1510725}
        # },

        'Bartolini, m': {
            'query_str': 'Bartolini, m', 'expected_recids': {1617696}
        },
        # 'Christian Maes': {
        #     # Should not match 1245957.
        #     'query_str': 'Christian Maes', 'expected_recids': {682478, 1367322}
        # }

        'RODriguez-gomez': {
            'query_str': 'RODriguez-gomez', 'expected_recids': {1632970}
        },

        'van kooten': {
            'query_str': 'van kooten', 'expected_recids': {1629966, 1334686}
        },
        'silva, j r p': {
            'query_str': 'silva, j r p', 'expected_recids': {1251373, 1325169}
        }
    }
)
def test_authors_search(search_api_client, query_str, expected_recids):
    assert _query_and_retrieve_control_numbers(search_api_client, query_str) == expected_recids,\
        "Query was [" + query_str + "]"


def test_lastname_same_prefix_firstname(search_api_client):
    samuele_recids = _query_and_retrieve_control_numbers(search_api_client, 'Mele, Samuele')
    salvatore_recids = _query_and_retrieve_control_numbers(search_api_client, 'Mele, Salvatore')

    single_samuele_record = samuele_recids.difference(salvatore_recids).pop()

    assert single_samuele_record not in salvatore_recids
