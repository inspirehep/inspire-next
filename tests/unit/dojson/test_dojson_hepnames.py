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

from __future__ import absolute_import, division, print_function

import os
import pkg_resources

import pytest

from dojson.contrib.marc21.utils import create_record

from inspirehep.dojson.hepnames import hepnames2marc, hepnames
from inspirehep.dojson.utils import clean_record, get_recid_from_ref


@pytest.fixture
def marcxml_to_json():
    marcxml = pkg_resources.resource_string(__name__,
                                            os.path.join(
                                                'fixtures',
                                                'test_hepnames_record.xml'
                                            ))
    record = create_record(marcxml)
    return hepnames.do(record)


@pytest.fixture
def json_to_marc(marcxml_to_json):
    return hepnames2marc.do(marcxml_to_json)


def test_dates(marcxml_to_json, json_to_marc):
    """Test if dates is created correctly."""
    # TODO fix dojson to take dates from 100__d
    pass


def test_experiments(marcxml_to_json, json_to_marc):
    """Test if experiments is created correctly."""
    assert (marcxml_to_json['experiments'][1]['name'] ==
            json_to_marc['693'][1]['e'])
    assert (marcxml_to_json['experiments'][1]['start_year'] ==
            json_to_marc['693'][1]['s'])
    assert (marcxml_to_json['experiments'][1]['end_year'] ==
            json_to_marc['693'][1]['d'])
    assert (marcxml_to_json['experiments'][1]['status'] ==
            json_to_marc['693'][1]['z'])


def test_field_categories(marcxml_to_json, json_to_marc):
    """Test if field_categories is created correctly."""
    assert (marcxml_to_json['field_categories'][0]['term'] ==
            json_to_marc['65017'][0]['a'])
    assert (marcxml_to_json['field_categories'][1]['term'] ==
            json_to_marc['65017'][1]['a'])
    assert (json_to_marc['65017'][1]['2'] == 'INSPIRE')


def test_ids(marcxml_to_json, json_to_marc):
    """Test if ids is created correctly."""
    assert (marcxml_to_json['ids'][0]['value'] ==
            json_to_marc['035'][0]['a'])
    assert (marcxml_to_json['ids'][0]['type'] ==
            json_to_marc['035'][0]['9'])
    assert (marcxml_to_json['ids'][1]['value'] ==
            json_to_marc['035'][1]['a'])
    assert (marcxml_to_json['ids'][1]['type'] ==
            json_to_marc['035'][1]['9'])


def test_ids_from_double_035__a_9():
    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">INSPIRE-00134135</subfield>'
        '    <subfield code="9">INSPIRE</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="a">H.Vogel.1</subfield>'
        '    <subfield code="9">BAI</subfield>'
        '  </datafield>'
        '</record>'
    )

    expected = [
        {
            'type': 'INSPIRE ID',
            'value': 'INSPIRE-00134135',
        },
        {
            'type': 'INSPIRE BAI',
            'value': 'H.Vogel.1',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_orcid():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">ORCID</subfield>'
        '  <subfield code="a">0000-0001-6771-2174</subfield>'
        '</datafield>'
    )

    expected = [
        {
            'type': 'ORCID',
            'value': '0000-0001-6771-2174',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_cern():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">CERN</subfield>'
        '  <subfield code="a">CERN-622961</subfield>'
        '</datafield>'
    )  # record/1064570/export/xme

    expected = [
        {
            'type': 'CERN',
            'value': 'CERN-622961',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_cern_malformed():
    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CERN-CERN-645257</subfield>'
        '  </datafield>'  # record/1030771/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">cern-783683</subfield>'
        '  </datafield>'  # record/1408145/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CERM-724319</subfield>'
        '  </datafield>'  # record/1244430/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CNER-727986</subfield>'
        '  </datafield>'  # record/1068077/export/xme
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">CERN</subfield>'
        '    <subfield code="a">CVERN-765559</subfield>'
        '  </datafield>'  # record/1340631/export/xme
        '</record>'
    )

    expected = [
        {
            'type': 'CERN',
            'value': 'CERN-645257',
        },
        {
            'type': 'CERN',
            'value': 'CERN-783683',
        },
        {
            'type': 'CERN',
            'value': 'CERN-724319',
        },
        {
            'type': 'CERN',
            'value': 'CERN-727986',
        },
        {
            'type': 'CERN',
            'value': 'CERN-765559',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_desy():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">DESY-1001805</subfield>'
        '  <subfield code="9">DESY</subfield>'
        '</datafield>'
    )  # record/993224/export/xme

    expected = [
        {
            'type': 'DESY',
            'value': 'DESY-1001805',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_wikipedia():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">Wikipedia</subfield>'
        '  <subfield code="a">Guido_Tonelli</subfield>'
        '</datafield>'
    )  # record/985898/export/xme

    expected = [
        {
            'type': 'WIKIPEDIA',
            'value': 'Guido_Tonelli',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_slac():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SLAC</subfield>'
        '  <subfield code="a">SLAC-218626</subfield>'
        '</datafield>'
    )  # record/1028379/export/xme

    expected = [
        {
            'type': 'SLAC',
            'value': 'SLAC-218626',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_with_bai():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="a">Jian.Long.Han.1</subfield>'
        '</datafield>'
    )  # record/1464894/export/xme

    expected = [
        {
            'type': 'INSPIRE BAI',
            'value': 'Jian.Long.Han.1',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_double_035__a_9_with_kaken():
    snippet = (
        '<record>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">BAI</subfield>'
        '    <subfield code="a">Toshio.Suzuki.2</subfield>'
        '  </datafield>'
        '  <datafield tag="035" ind1=" " ind2=" ">'
        '    <subfield code="9">KAKEN</subfield>'
        '    <subfield code="a">70139070</subfield>'
        '  </datafield>'
        '</record>'
    )  # record/1474271/export/xme

    expected = [
        {
            'type': 'INSPIRE BAI',
            'value': 'Toshio.Suzuki.2',
        },
        {
            'type': 'KAKEN',
            'value': 'KAKEN-70139070',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_googlescholar():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">GoogleScholar</subfield>'
        '  <subfield code="a">Tnl-9KoAAAAJ</subfield>'
        '</datafield>'
    )  # record/1467553/export/xme

    expected = [
        {
            'type': 'GOOGLESCHOLAR',
            'value': 'Tnl-9KoAAAAJ',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_viaf():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">VIAF</subfield>'
        '  <subfield code="a">34517183</subfield>'
        '</datafield>'
    )  # record/1008109/export/xme

    expected = [
        {
            'type': 'VIAF',
            'value': '34517183',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_researcherid():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">RESEARCHERID</subfield>'
        '  <subfield code="a">B-4717-2008</subfield>'
        '</datafield>'
    )  # record/1051026/export/xme

    expected = [
        {
            'type': 'RESEARCHERID',
            'value': 'B-4717-2008',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__a_9_with_scopus():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">SCOPUS</subfield>'
        '  <subfield code="a">7103280792</subfield>'
        '</datafield>'
    )  # record/1017182/export/xme

    expected = [
        {
            'type': 'SCOPUS',
            'value': '7103280792',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['ids']


def test_ids_from_035__9():
    snippet = (
        '<datafield tag="035" ind1=" " ind2=" ">'
        '  <subfield code="9">INSPIRE</subfield>'
        '</datafield>'
    )  # record/edit/?ln=en#state=edit&recid=1474355&recrev=20160707223728

    result = clean_record(hepnames.do(create_record(snippet)))

    assert 'ids' not in result


def test_name(marcxml_to_json, json_to_marc):
    """Test if name is created correctly."""
    assert (marcxml_to_json['name']['value'] ==
            json_to_marc['100']['a'])
    assert (marcxml_to_json['name']['numeration'] ==
            json_to_marc['100']['b'])
    assert (marcxml_to_json['name']['title'] ==
            json_to_marc['100']['c'])
    assert (marcxml_to_json['name']['status'] ==
            json_to_marc['100']['g'])
    assert (marcxml_to_json['name']['preferred_name'] ==
            json_to_marc['100']['q'])


def test_native_name(marcxml_to_json, json_to_marc):
    """Test if native_name is created correctly."""
    assert (marcxml_to_json['native_name'] ==
            json_to_marc['880']['a'])


def test_other_names(marcxml_to_json, json_to_marc):
    """Test if other_names is created correctly."""
    assert (marcxml_to_json['other_names'][0] ==
            json_to_marc['400'][0]['a'])
    assert (marcxml_to_json['other_names'][1] ==
            json_to_marc['400'][1]['a'])


def test_other_names_from_400__triple_a():
    snippet = (
        '<datafield tag="400" ind1=" " ind2=" ">'
        '  <subfield code="a">Yosef Cohen, Hadar</subfield>'
        '  <subfield code="a">Josef Cohen, Hadar</subfield>'
        '  <subfield code="a">Cohen, Hadar Josef</subfield>'
        '</datafield>'
    )  # record/1292399/export/xme

    expected = [
        'Yosef Cohen, Hadar',
        'Josef Cohen, Hadar',
        'Cohen, Hadar Josef',
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['other_names']


def test_advisors(marcxml_to_json, json_to_marc):
    assert (marcxml_to_json['advisors'][0]['name'] ==
            json_to_marc['701'][0]['a'])
    assert (marcxml_to_json['advisors'][0]['_degree_type'] ==
            json_to_marc['701'][0]['g'])


def test_advisors_from_701__a_g_i():
    snippet = (
        '<datafield tag="701" ind1=" " ind2=" ">'
        '  <subfield code="a">Rivelles, Victor O.</subfield>'
        '  <subfield code="g">PhD</subfield>'
        '  <subfield code="i">INSPIRE-00120420</subfield>'
        '  <subfield code="x">991627</subfield>'
        '  <subfield code="y">1</subfield>'
        '</datafield>'
    )  # record/1474091

    expected = [
        {
            'name': 'Rivelles, Victor O.',
            'degree_type': 'PhD',
            '_degree_type': 'PhD',
            'record': {
                '$ref': 'http://localhost:5000/api/authors/991627',
            },
            'curated_relation': True
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['advisors']


def test_positions(marcxml_to_json, json_to_marc):
    """Test if positions is created correctly."""
    assert (marcxml_to_json['positions'][0]['institution']['name'] ==
            json_to_marc['371'][0]['a'])
    assert (marcxml_to_json['positions'][0]['_rank'] ==
            json_to_marc['371'][0]['r'])
    assert (marcxml_to_json['positions'][0]['start_date'] ==
            json_to_marc['371'][0]['s'])
    assert (marcxml_to_json['positions'][0]['email'] ==
            json_to_marc['371'][0]['m'])
    assert (marcxml_to_json['positions'][0]['status'] ==
            json_to_marc['371'][0]['z'])
    assert (marcxml_to_json['positions'][1]['end_date'] ==
            json_to_marc['371'][1]['t'])
    assert (marcxml_to_json['positions'][2]['old_email'] ==
            json_to_marc['371'][2]['o'])


def test_positions_from_371__a():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Aachen, Tech. Hochsch.</subfield>'
        '</datafield>'
    )  # record/997958

    expected = [
        {
            'curated_relation': False,
            'institution': {
                'name': 'Aachen, Tech. Hochsch.',
            },
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['positions']


def test_positions_from_371__a_m_r_z():
    snippet = (
        '<datafield tag="371" ind1=" " ind2=" ">'
        '  <subfield code="a">Antwerp U.</subfield>'
        '  <subfield code="m">pierre.vanmechelen@ua.ac.be</subfield>'
        '  <subfield code="r">SENIOR</subfield>'
        '  <subfield code="z">Current</subfield>'
        '</datafield>'
    )  # record/997958

    expected = [
        {
            'curated_relation': False,
            'email': 'pierre.vanmechelen@ua.ac.be',
            'institution': {
                'name': 'Antwerp U.',
            },
            'rank': 'SENIOR',
            '_rank': 'SENIOR',
            'status': 'Current',
        },
    ]
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['positions']


def test_private_current_emails(marcxml_to_json, json_to_marc):
    """Test if private_current_emails is created correctly."""
    assert (marcxml_to_json['private_current_emails'][0] ==
            json_to_marc['595'][1]['m'])


def test_private_old_emails(marcxml_to_json, json_to_marc):
    """Test if private_old_emails is created correctly."""
    assert (marcxml_to_json['private_old_emails'][0] ==
            json_to_marc['595'][0]['o'])


def test_private_notes(marcxml_to_json, json_to_marc):
    """Test if private_notes is created correctly."""
    assert (marcxml_to_json['_private_note'][0] ==
            json_to_marc['595'][2]['a'])


def test_prizes(marcxml_to_json, json_to_marc):
    """Test if prizes is created correctly."""
    assert (marcxml_to_json['prizes'][0] ==
            json_to_marc['678'][0]['a'])


def test_source(marcxml_to_json, json_to_marc):
    """Test if source is created correctly."""
    assert (marcxml_to_json['source'][0]['name'] ==
            json_to_marc['670'][0]['a'])
    assert (marcxml_to_json['source'][1]['date_verified'] ==
            json_to_marc['670'][1]['d'])


def test_urls(marcxml_to_json, json_to_marc):
    """Test if urls is created correctly."""
    assert (marcxml_to_json['urls'][0]['value'] ==
            json_to_marc['8564'][0]['u'])
    assert (marcxml_to_json['urls'][0]['description'] ==
            json_to_marc['8564'][0]['y'])


def test_acquisition_source_field():
    """Test acquisition_source."""
    snippet = (
        '<record>'
        '   <datafield tag="541" ind1=" " ind2=" ">'
        '       <subfield code="a">inspire:uid:50000</subfield>'
        '       <subfield code="b">example@gmail.com</subfield>'
        '       <subfield code="c">submission</subfield>'
        '       <subfield code="d">2015-12-10</subfield>'
        '       <subfield code="e">339830</subfield>'
        '   </datafield>'
        '</record>'
    )

    expected = {
        'source': "inspire:uid:50000",
        'email': "example@gmail.com",
        'method': "submission",
        'date': "2015-12-10",
        'submission_number': "339830",
    }
    result = clean_record(hepnames.do(create_record(snippet)))

    assert expected == result['acquisition_source']


def test_acquisition_source_field_marcxml():
    """Test acquisition_source MARC output."""
    expected = {
        'a': 'inspire:uid:50000',
        'c': 'submission',
        'b': 'example@gmail.com',
        'e': '339830',
        'd': '2015-12-10'
    }

    record = {"acquisition_source": {
        'source': "inspire:uid:50000",
        'email': "example@gmail.com",
        'method': "submission",
        'date': "2015-12-10",
        'submission_number': "339830",
    }}
    result = hepnames2marc.do(record)
    assert expected == result['541']
