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
import os
import pkg_resources

from inspirehep.modules.orcid import OrcidConverter
from lxml import etree


def valid_against_schema(xml):
    """Validate xml schema."""
    schema_path = pkg_resources.resource_filename(
        __name__, os.path.join('fixtures', 'record_2.0', 'work-2.0.xsd')
    )
    schema = etree.XMLSchema(file=schema_path)
    schema.assertValid(xml)
    return True


def xml_parse(xml_string):
    """Parse an ``xml_string`` into XML."""
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.fromstring(xml_string, parser)


def xml_compare(expected, result):
    """Assert two XML nodes equal."""
    assert etree.tostring(result, pretty_print=True) == \
        etree.tostring(expected, pretty_print=True)
    return True


def test_format_article(app, api_client):
    response = api_client.get('/literature/4328')
    assert response.status_code == 200
    article = json.loads(response.data)

    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>Partial Symmetries of Weak Interactions</common:title>
        </work:title>
        <work:journal-title>Nucl.Phys.</work:journal-title>
        <work:type>journal-article</work:type>
        <common:publication-date>
            <common:year>1961</common:year>
        </common:publication-date>
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>doi</common:external-id-type>
                <common:external-id-value>10.1016/0029-5582(61)90469-2</common:external-id-value>
                <common:external-id-url>https://doi.org/10.1016/0029-5582(61)90469-2</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
        <work:url>http://inspirehep.net/record/4328</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>Glashow, S.L.</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    result = OrcidConverter(
        article['metadata'],
        url_pattern='http://inspirehep.net/record/{recid}',
    ).get_xml()
    assert valid_against_schema(result)
    assert xml_compare(expected, result)


def test_format_conference_paper(app, api_client):
    response = api_client.get('/literature/524480')
    assert response.status_code == 200
    inproceedings = json.loads(response.data)

    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>CMB anisotropies: A Decadal survey</common:title>
        </work:title>
        <work:journal-title>4th RESCEU International Symposium on Birth and Evolution of the Universe</work:journal-title>
        <work:type>conference-paper</work:type>
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>arxiv</common:external-id-type>
                <common:external-id-value>astro-ph/0002520</common:external-id-value>
                <common:external-id-url>http://arxiv.org/abs/astro-ph/0002520</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
        <work:url>http://inspirehep.net/record/524480</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>Hu, Wayne</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    result = OrcidConverter(
        inproceedings['metadata'],
        url_pattern='http://inspirehep.net/record/{recid}',
    ).get_xml()
    assert valid_against_schema(result)
    assert xml_compare(expected, result)


def test_format_proceedings(app, api_client):
    response = api_client.get('/literature/701585')
    assert response.status_code == 200
    proceedings = json.loads(response.data)

    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>HERA and the LHC: A Workshop on the implications of HERA for LHC physics: Proceedings Part A</common:title>
        </work:title>
        <work:type>edited-book</work:type>
        <common:publication-date>
            <common:year>2005</common:year>
        </common:publication-date>
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>arxiv</common:external-id-type>
                <common:external-id-value>hep-ph/0601012</common:external-id-value>
                <common:external-id-url>http://arxiv.org/abs/hep-ph/0601012</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
        <work:url>http://inspirehep.net/record/701585</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>De Roeck, A.</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>editor</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
            <work:contributor>
                <work:credit-name>Jung, H.</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>additional</work:contributor-sequence>
                    <work:contributor-role>editor</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    result = OrcidConverter(
        proceedings['metadata'],
        url_pattern='http://inspirehep.net/record/{recid}',
    ).get_xml()
    assert valid_against_schema(result)
    assert xml_compare(expected, result)


def test_format_thesis(app, api_client):
    response = api_client.get('/literature/1395663')
    assert response.status_code == 200
    phdthesis = json.loads(response.data)

    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>MAGIC $\\gamma$-ray observations of distant AGN and a study of source variability and the extragalactic background light using FERMI and air Cherenkov telescopes</common:title>
        </work:title>
        <work:type>dissertation</work:type>
        <work:url>http://inspirehep.net/record/1395663</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>Mankuzhiyil, Nijil</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    result = OrcidConverter(
        phdthesis['metadata'],
        url_pattern='http://inspirehep.net/record/{recid}',
    ).get_xml()
    assert valid_against_schema(result)
    assert xml_compare(expected, result)


def test_format_book(app, api_client):
    response = api_client.get('/literature/736770')
    assert response.status_code == 200
    book = json.loads(response.data)

    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>Differential geometry and Lie groups for physicists</common:title>
        </work:title>
        <work:type>book</work:type>
        <common:publication-date>
            <common:year>2011</common:year>
            <common:month>03</common:month>
            <common:day>03</common:day>
        </common:publication-date>
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>isbn</common:external-id-type>
                <common:external-id-value>9780521187961</common:external-id-value>
            </common:external-id>
            <common:external-id>
                <common:external-id-type>isbn</common:external-id-type>
                <common:external-id-value>9780521845076</common:external-id-value>
            </common:external-id>
            <common:external-id>
                <common:external-id-type>isbn</common:external-id-type>
                <common:external-id-value>9780511242960</common:external-id-value>
            </common:external-id>
        </common:external-ids>
        <work:url>http://inspirehep.net/record/736770</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>Fecko, M.</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    result = OrcidConverter(
        book['metadata'],
        url_pattern='http://inspirehep.net/record/{recid}',
    ).get_xml()
    assert valid_against_schema(result)
    assert xml_compare(expected, result)


def test_format_book_chapter(app, api_client):
    response = api_client.get('/literature/1375491')
    assert response.status_code == 200
    inbook = json.loads(response.data)

    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>Supersymmetry</common:title>
        </work:title>
        <work:type>book-chapter</work:type>
        <common:publication-date>
            <common:year>2015</common:year>
        </common:publication-date>
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>doi</common:external-id-type>
                <common:external-id-value>10.1007/978-3-319-15001-7_10</common:external-id-value>
                <common:external-id-url>https://doi.org/10.1007/978-3-319-15001-7_10</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
            <common:external-id>
                <common:external-id-type>arxiv</common:external-id-type>
                <common:external-id-value>1506.03091</common:external-id-value>
                <common:external-id-url>http://arxiv.org/abs/1506.03091</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
        <work:url>http://inspirehep.net/record/1375491</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>Bechtle, Philip</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
            <work:contributor>
                <work:credit-name>Plehn, Tilman</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>additional</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
                <work:contributor>
                <work:credit-name>Sander, Christian</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>additional</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    result = OrcidConverter(
        inbook['metadata'],
        url_pattern='http://inspirehep.net/record/{recid}',
    ).get_xml()
    assert valid_against_schema(result)
    assert xml_compare(expected, result)


def test_format_thesis_with_author_orcid(app, api_client):
    response = api_client.get('/literature/1395663')
    assert response.status_code == 200
    phdthesis = json.loads(response.data)

    phdthesis['metadata']['authors'][0]['ids'] = [
        {
            'schema': 'ORCID',
            'value': '0000-0002-1825-0097',
        }
    ]
    phdthesis['metadata']['authors'][0]['emails'] = ['email@fake-domain.local']

    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>MAGIC $\\gamma$-ray observations of distant AGN and a study of source variability and the extragalactic background light using FERMI and air Cherenkov telescopes</common:title>
        </work:title>
        <work:type>dissertation</work:type>
        <work:url>http://inspirehep.net/record/1395663</work:url>
        <work:contributors>
            <work:contributor>
                <common:contributor-orcid>
                    <common:uri>http://orcid.org/0000-0002-1825-0097</common:uri>
                    <common:path>0000-0002-1825-0097</common:path>
                    <common:host>orcid.org</common:host>
                </common:contributor-orcid>
                <work:credit-name>Mankuzhiyil, Nijil</work:credit-name>
                <work:contributor-email>email@fake-domain.local</work:contributor-email>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    result = OrcidConverter(
        phdthesis['metadata'],
        url_pattern='http://inspirehep.net/record/{recid}',
    ).get_xml()
    assert valid_against_schema(result)
    assert xml_compare(expected, result)
