# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
#
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Tests for Bibfield to doJSON conversion."""

import json
import os
import pkg_resources
import pytest

from inspirehep.dojson.bibfield import bibfield


@pytest.fixture
def hep_bibfield():
    return json.loads(
        pkg_resources.resource_string(
            'tests',
            os.path.join(
                'fixtures',
                'test_bibfield_record.json'
            )
        )
    )


@pytest.fixture
def record(hep_bibfield):
    return bibfield.do(hep_bibfield)


def test_abstract(hep_bibfield, record):
    """Test if abstract is created correctly"""
    assert (
        hep_bibfield['abstract']['summary'] ==
        record['abstracts'][0]['value']
    )


def test_system_number_external(hep_bibfield, record):
    """Test if system_number_external is created correctly"""
    assert (
        hep_bibfield['system_number_external'] ==
        record['external_system_numbers'][0]
    )


def test_subject_term(hep_bibfield, record):
    """Test if subject_term is created correctly"""
    assert (
        hep_bibfield['subject_term'] ==
        record['subject_terms']
    )


def test_acquisition_source(hep_bibfield, record):
    """Test if acquisition_source is created correctly"""
    assert (
        hep_bibfield['acquisition_source'] ==
        record['acquisition_source']
    )


def test_collections(hep_bibfield, record):
    """Test if collections is created correctly"""
    assert (
        hep_bibfield['collections'] ==
        record['collections']
    )


def test_fft(hep_bibfield, record):
    """Test if fft is created correctly"""
    assert (
        hep_bibfield['fft'] ==
        record['fft']
    )


def test_license(hep_bibfield, record):
    """Test if license is created correctly"""
    assert (
        hep_bibfield['license'] ==
        record['license']
    )


def test_page_nr(hep_bibfield, record):
    """Test if page_nr is created correctly"""
    assert (
        hep_bibfield['page_nr'] ==
        record['page_nr']
    )


def test_references(hep_bibfield, record):
    """Test if references is created correctly"""
    assert (
        hep_bibfield['reference'] ==
        record['references']
    )


def test_edition(hep_bibfield, record):
    """Test if edition is created correctly"""
    assert (
        hep_bibfield['edition'] ==
        record['edition']
    )


def test_report_numbers(hep_bibfield, record):
    """Test if report_numbers is created correctly"""
    assert (
        hep_bibfield['report_number'][0]['primary'] ==
        record['report_numbers'][0]['value']
    )
    assert (
        hep_bibfield['report_number'][0]['source'] ==
        record['report_numbers'][0]['source']
    )


def test_refextract(hep_bibfield, record):
    """Test if refextract is created correctly"""
    assert (
        hep_bibfield['refextract'] ==
        record['refextract']
    )


def test_doi(hep_bibfield, record):
    """Test if doi is created correctly"""
    assert (
        hep_bibfield['doi'] ==
        record['dois'][0]['value']
    )


def test_subject_terms(hep_bibfield, record):
    """Test if subject_terms is created correctly"""
    assert (
        hep_bibfield['subject_term'] ==
        record['subject_terms']
    )


def test_breadcrumb_title(hep_bibfield, record):
    """Test if breadcrumb_title is created correctly"""
    assert (
        hep_bibfield['title']['title'] ==
        record['breadcrumb_title']
    )


def test_corporate_author(hep_bibfield, record):
    """Test if corporate_author is created correctly"""
    assert (
        hep_bibfield['corporate_author'] ==
        record['corporate_author'][0]
    )


def test_collaboration(hep_bibfield, record):
    """Test if collaboration is created correctly"""
    assert (
        hep_bibfield['collaboration'] ==
        record['collaboration'][0]['value']
    )


def test_preprint_date(hep_bibfield, record):
    """Test if preprint_date is created correctly"""
    assert (
        hep_bibfield['preprint_info']['date'] ==
        record['preprint_date']
    )


def test_hidden_notes(hep_bibfield, record):
    """Test if hidden_notes is created correctly"""
    assert (
        hep_bibfield['hidden_note'][0]['value'] ==
        record['hidden_notes'][0]['value']
    )
    assert (
        hep_bibfield['hidden_note'][0]['source'] ==
        record['hidden_notes'][0]['source']
    )


def test_public_notes(hep_bibfield, record):
    """Test if public_notes is created correctly"""
    assert (
        hep_bibfield['note'] ==
        record['public_notes']
    )


def test_imprints(hep_bibfield, record):
    """Test if imprints is created correctly"""
    assert (
        hep_bibfield['imprint'] ==
        record['imprints'][0]
    )


def test_oai_pmh(hep_bibfield, record):
    """Test if oai_pmh is created correctly"""
    assert (
        hep_bibfield['oai_pmh'] ==
        record['oai_pmh']
    )


def test_thesis(hep_bibfield, record):
    """Test if thesis is created correctly"""
    assert (
        hep_bibfield['thesis']['university'] ==
        record['thesis']['university']
    )
    assert (
        hep_bibfield['thesis']['date'] ==
        record['thesis']['date']
    )
    assert (
        hep_bibfield['defense_date'] ==
        record['thesis']['defense_date']
    )


def test_isbn(hep_bibfield, record):
    """Test if isbn is created correctly"""
    assert (
        hep_bibfield['isbn'] ==
        record['isbns']
    )


def test_url(hep_bibfield, record):
    """Test if url is created correctly"""
    assert (
        hep_bibfield['url'] ==
        record['urls'][0]
    )


def test_publication_info(hep_bibfield, record):
    """Test if publication_info is created correctly"""
    assert (
        hep_bibfield['publication_info'] ==
        record['publication_info'][0]
    )


def test_free_keywords(hep_bibfield, record):
    """Test if free_keywords is created correctly"""
    assert (
        hep_bibfield['free_keyword'] ==
        record['free_keywords']
    )


def test_languages(hep_bibfield, record):
    """Test if language is created correctly"""
    assert (
        hep_bibfield['language'] ==
        record['languages'][0]
    )


def test_titles_old(hep_bibfield, record):
    """Test if titles_old is created correctly"""
    assert (
        hep_bibfield['title_old']['main'] ==
        record['titles_old'][0]['title']
    )
    assert (
        hep_bibfield['title_old']['subtitle'] ==
        record['titles_old'][0]['subtitle']
    )


def test_thesaurus_terms(hep_bibfield, record):
    """Test if thesaurus_terms is created correctly"""
    assert (
        hep_bibfield['thesaurus_terms'][0]['keyword'] ==
        record['thesaurus_terms'][0]['keyword']
    )
    assert (
        hep_bibfield['thesaurus_terms'][0]['classification_scheme'] ==
        record['thesaurus_terms'][0]['scheme']
    )


def test_thesis_supervisor(hep_bibfield, record):
    """Test if thesis_supervisor is created correctly"""
    assert (
        hep_bibfield['thesis_supervisor']['full_name'] ==
        record['thesis_supervisor'][0]['full_name']
    )
    assert (
        hep_bibfield['thesis_supervisor']['affiliation'] ==
        record['thesis_supervisor'][0]['affiliation']['value']
    )


def test_spires_sysnos(hep_bibfield, record):
    """Test if spires_sysnos is created correctly"""
    assert (
        hep_bibfield['spires_sysno']['value'] ==
        record['spires_sysnos'][0]
    )


def test_title_translation(hep_bibfield, record):
    """Test if title_translation is created correctly"""
    assert (
        hep_bibfield['title_translation']['value'] ==
        record['title_translation'][0]['title']
    )
    assert (
        hep_bibfield['title_translation']['subtitle'] ==
        record['title_translation'][0]['subtitle']
    )


def test_copyright(hep_bibfield, record):
    """Test if copyright is created correctly"""
    assert (
        hep_bibfield['coyright'] ==
        record['copyright']
    )


def test_accelerator_experiments(hep_bibfield, record):
    """Test if caccelerator_experiments is created correctly"""
    assert (
        hep_bibfield['accelerator_experiment'] ==
        record['accelerator_experiments'][0]
    )


def test_arxiv_eprints_and_system_numbers(hep_bibfield, record):
    """Test if arxiv_eprints is created correctly"""
    assert hep_bibfield['system_number_external']['value'] == record['arxiv_eprints'][0]['value']
    assert hep_bibfield['system_number_external']['value'] == record['external_system_numbers'][0]['value']


def test_title(hep_bibfield, record):
    """Test if title is created correctly"""
    assert hep_bibfield['title']['title'] == record['titles'][0]['title']
    assert hep_bibfield['title']['subtitle'] == record['titles'][0]['subtitle']
    assert hep_bibfield['title']['source'] == record['titles'][0]['source']


def test_authors(hep_bibfield, record):
    """Test if authors is created correctly"""
    all_authors = hep_bibfield['authors'] + \
        [hep_bibfield['_first_author']] + \
        hep_bibfield['_additional_authors']

    assert (len(all_authors),
            len(record['authors']))
    for author in all_authors:
        assert (
            author['full_name'] in
            [a['full_name'] for a in record['authors']]
        )
        assert (
            author['affiliation'] in
            [a['affiliations'][0]['value'] for a in record['authors']]
        )
        if "relator_term" in author:
            assert (
                author['relator_term'] in
                [a['role'] for a in record['authors']]
            )
        if "INSPIRE_id" in author:
            assert (
                author['INSPIRE_id'] in
                [a['inspire_id'] for a in record['authors']]
            )
