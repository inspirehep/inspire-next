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

from inspire_utils.date import PartialDate
from inspirehep.modules.orcid import OrcidBuilder
from lxml import etree


def xml_parse(xml_string):
    """Parse an ``xml_string`` into XML."""
    parser = etree.XMLParser(remove_blank_text=True)
    return etree.fromstring(xml_string, parser)


def xml_compare(result, expected):
    """Assert two XML nodes equal."""
    assert etree.tostring(result, pretty_print=True) == etree.tostring(expected, pretty_print=True)
    return True


def test_add_author():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:contributors>
            <work:contributor>
                <work:credit-name>Josiah Carberry</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
                <common:contributor-orcid>
                    <common:uri>http://orcid.org/0000-0002-1825-0097</common:uri>
                    <common:path>0000-0002-1825-0097</common:path>
                    <common:host>orcid.org</common:host>
                </common:contributor-orcid>
                <work:contributor-email>j.carberry@orcid.org</work:contributor-email>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_contributor("Josiah Carberry", "author", "0000-0002-1825-0097", "j.carberry@orcid.org")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_multiple_authors():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:contributors>
            <work:contributor>
                <work:credit-name>Josiah Carberry</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
                <common:contributor-orcid>
                    <common:uri>http://orcid.org/0000-0002-1825-0097</common:uri>
                    <common:path>0000-0002-1825-0097</common:path>
                    <common:host>orcid.org</common:host>
                </common:contributor-orcid>
                <work:contributor-email>j.carberry@orcid.org</work:contributor-email>
            </work:contributor>
            <work:contributor>
                <work:credit-name>Homer Simpson</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>additional</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_contributor("Josiah Carberry", "author", "0000-0002-1825-0097", "j.carberry@orcid.org")
    builder.add_contributor("Homer Simpson", "author")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_title():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>Developing Thin Clients Using Amphibious Epistemologies</common:title>
            <common:subtitle>Made-up subtitle</common:subtitle>
        </work:title>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_title("Developing Thin Clients Using Amphibious Epistemologies", "Made-up subtitle")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_publication_date():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <common:publication-date>
            <common:year>1996</common:year>
            <common:month>09</common:month>
            <common:day>07</common:day>
        </common:publication-date>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_publication_date(PartialDate(1996, 9, 7))
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_type():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:type>conference-paper</work:type>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_type("conference-paper")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_citation():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:citation>
            <work:citation-type>bibtex</work:citation-type>
            <work:citation-value>@article{...}</work:citation-value>
        </work:citation>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_citation("bibtex", "@article{...}")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_country_code():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <common:country>CH</common:country>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_country("CH")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_external_id():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>doi</common:external-id-type>
                <common:external-id-value>10.1087/20120404</common:external-id-value>
                <common:external-id-url>https://doi.org/10.1087/20120404</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_external_id("doi", "10.1087/20120404", "https://doi.org/10.1087/20120404", "self")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_multiple_external_ids():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>doi</common:external-id-type>
                <common:external-id-value>10.5555/12345679</common:external-id-value>
                <common:external-id-url>https://doi.org/10.5555/12345679</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
            <common:external-id>
                <common:external-id-type>issn</common:external-id-type>
                <common:external-id-value>0264-3561</common:external-id-value>
                <common:external-id-relationship>part-of</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_doi("10.5555/12345679", "self")
    builder.add_external_id("issn", "0264-3561", relationship="part-of")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_journal_title():
    expected = xml_parse(u"""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:journal-title>JHEP</work:journal-title>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_journal_title("JHEP")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_title_translation():
    expected = xml_parse(u"""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:title>
            <common:title>Developing Thin Clients Using Amphibious Epistemologies</common:title>
            <common:translated-title language-code="es">Desarrollo de clientes ligeros que utilizan epistemolog&#237;as anfibias</common:translated-title>
        </work:title>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_title("Developing Thin Clients Using Amphibious Epistemologies",
                      translated_title=(u"Desarrollo de clientes ligeros que utilizan epistemologías anfibias", "es"))
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_add_url():
    expected = xml_parse("""
    <work:work xmlns:common="http://www.orcid.org/ns/common" xmlns:work="http://www.orcid.org/ns/work">
        <work:url>http://example.org</work:url>
    </work:work>
    """)

    builder = OrcidBuilder()
    builder.add_url("http://example.org")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_set_visibility():
    expected = xml_parse("""
    <work:work
        xmlns:common="http://www.orcid.org/ns/common"
        xmlns:work="http://www.orcid.org/ns/work"
        visibility="public" />
    """)

    builder = OrcidBuilder()
    builder.set_visibility("public")
    result = builder.get_xml()

    assert xml_compare(result, expected)


def test_set_put_code():
    expected = xml_parse("""
    <work:work
        xmlns:common="http://www.orcid.org/ns/common"
        xmlns:work="http://www.orcid.org/ns/work"
        put-code="123456" />
    """)

    builder = OrcidBuilder()
    builder.set_put_code(123456)
    result = builder.get_xml()

    assert xml_compare(result, expected)
