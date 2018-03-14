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

from inspirehep.modules.authors.utils import (
    bai,
    get_author_record_from_xml_response,
)


def test_that_bai_conforms_to_the_spec():
    assert bai("Ellis, Jonathan Richard") == "J.R.Ellis"
    assert bai("ellis, jonathan richard") == "J.R.Ellis"
    assert bai("ELLIS, JONATHAN RICHARD") == "J.R.Ellis"
    assert bai("Ellis, John Richard") == "J.R.Ellis"
    assert bai("Ellis, J R") == "J.R.Ellis"
    assert bai("Ellis, J. R.") == "J.R.Ellis"
    assert bai("Ellis, J.R.") == "J.R.Ellis"
    assert bai("Ellis, J.R. (Jr)") == "J.R.Ellis"
    assert bai("Ellis") == "Ellis"
    assert bai("Ellis, ") == "Ellis"
    assert bai("O'Connor, David") == "D.OConnor"
    assert bai("o'connor, david") == "D.OConnor"
    assert bai("McCurdy, David") == "D.McCurdy"
    assert bai("DeVito, Dany") == "D.DeVito"
    assert bai("DEVITO, Dany") == "D.Devito"
    assert bai("De Villiers, Jean-Pierre") == "J.P.de.Villiers"
    assert bai("Höing, Rebekka Sophie") == "R.S.Hoeing"
    assert bai("Müller, Andreas") == "A.Mueller"
    assert bai("Hernández-Tomé, G.") == "G.Hernandez.Tome"
    assert bai("José de Goya y Lucientes, Francisco Y H") == "F.Y.H.Jose.de.Goya.y.Lucientes"


def test_get_author_record_from_xml_response():
    xml = """<?xml version="1.0" encoding="UTF-8"?>\n
    <collection
        xmlns="http://www.loc.gov/MARC21/slim">\n
        <record>\n
            <datafield tag="100" ind1=" " ind2=" ">\n
                <subfield code="a">Aab, Alexander</subfield>\n
            </datafield>\n
            <datafield tag="980" ind1=" " ind2=" ">\n
                <subfield code="a">HEPNAMES</subfield>\n
            </datafield>\n
            <datafield tag="980" ind1=" " ind2=" ">\n
                <subfield code="a">USEFUL</subfield>\n
            </datafield>\n
        </record>\n
    </collection>"""

    expected = {
        '$schema': 'authors.json',
        '_collections': ['Authors'],
        'deleted': False,
        'name': {'value': 'Aab, Alexander'},
        'stub': False
    }

    result = get_author_record_from_xml_response(xml)

    assert result == expected


def test_get_author_record_from_xml_response_fails_if_wrong_collection():
    xml = """<?xml version="1.0" encoding="UTF-8"?>\n
    <collection
        xmlns="http://www.loc.gov/MARC21/slim">\n
        <record>\n
            <datafield tag="245" ind1=" " ind2=" ">\n
                <subfield code="a">Gravitational Waves in Doubly Coupled Bigravity</subfield>\n
                <subfield code="9">arXiv</subfield>\n
            </datafield>\n
            <datafield tag="980" ind1=" " ind2=" ">\n
                <subfield code="a">HEP</subfield>\n
            </datafield>\n
            <datafield tag="980" ind1=" " ind2=" ">\n
                <subfield code="a">Published</subfield>\n
            </datafield>\n
        </record>\n
    </collection>"""

    result = get_author_record_from_xml_response(xml)

    assert not result


def test_get_author_record_from_xml_response_fails_if_no_record():
    xml = """<?xml version="1.0" encoding="UTF-8"?>\n
    <collection xmlns="http://www.loc.gov/MARC21/slim">\n\n
    </collection>"""

    result = get_author_record_from_xml_response(xml)

    assert not result
