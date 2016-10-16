# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from inspirehep.modules.relations import current_db_session
from inspirehep.modules.relations.command_producers import (
    match_record,
    render_query
    )
from inspirehep.modules.relations.model.relations import (
    AUTHORED_BY,
    AFFILIATED_WITH,
    CONTRIBUTED_TO,
    IS_ABOUT_EXPERIMENT,
    REFERS_TO,
    WRITTEN_BY
    )
from inspirehep.modules.relations.utils import pick_one_citation_type


class LiteratureRelationsSearch(object):

    @classmethod
    def _process_paper(cls, paper):
        return {
            "inspire_id": paper['control_number'],
            "citation_count": paper['citation_count'],
            "title": paper['title'],
            "year": paper['date'].split('-')[0]
        }


    @classmethod
    def get_references_summary(cls, recid, limit=None):
        limit_command = ''
        if limit:
            limit_command = ' LIMIT {}'.format(limit)

        query_elements = [
            match_record(recid, 'record'),
            'MATCH (record) - [:' + REFERS_TO + '] -> (reference)',
            ('WITH reference.recid as control_number, '
             'reference.earliest_date as date, reference.title as title, '
             'size((reference)<- [:' + REFERS_TO + '] - ()) as citation_count'
            ),
            'RETURN control_number, date, title, citation_count',
            limit_command
        ]

        query = render_query(query_elements)
        response = [record for record in current_db_session.run(query)]

        return map(cls._process_paper, response)


    @classmethod
    def get_citations_summary(cls, recid, limit=None):
        limit_command = ''
        if limit:
            limit_command = ' LIMIT {}'.format(limit)

        query_elements = [
            match_record(recid, 'record'),
            'MATCH (record) <- [:' + REFERS_TO + '] -> (citation)',
            ('WITH citation.recid as control_number, '
             'citation.earliest_date as date, citation.title as title, '
             'size((citation)<- [:' + REFERS_TO + '] - ()) as citation_count'
            ),
            'RETURN control_number, date, title, citation_count',
            limit_command
        ]

        query = render_query(query_elements)
        response = [record for record in current_db_session.run(query)]

        return map(cls._process_paper, response)


    @classmethod
    def get_impact_graph_summary(cls, recid, limit=None):

        return {
            'citations': cls.get_citations_summary(recid, limit),
            'references': cls.get_references_summary(recid, limit)
        }


class CitationSummarySearch(object):

    @classmethod
    def query_for_citation_summary_of_a_paper(cls):
        return (
             'OPTIONAL MATCH (paper) <- [:' + REFERS_TO + '] - '
            '(citation:Literature) '
            'WITH paper, citation, '
            'size('
            '(paper) - [:' + WRITTEN_BY + '] -> (:Person)'
            ' <- [:' + WRITTEN_BY + '] - (citation)'
            ') > 0 as self_citation '
            'WITH {cited_paper_id: paper.recid, '
            'cited_paper_date: paper.earliest_date, '
            'cited_subject: paper._display_research_field, '
            'cited_labels: labels(paper)} as cited_paper, '
            '(CASE citation WHEN NOT exists(citation.recid) THEN NULL '
            'ELSE'
            '{citing_paper_id: citation.recid, '
            'citation_date: citation.earliest_date, '
            'self_citation: self_citation, '
            'citation_subject: citation._display_research_field, '
            'citing_labels: labels(citation)} END) as citing_paper '
            'RETURN cited_paper, collect(citing_paper) as citing_papers'
        )


    @classmethod
    def query_to_match_all_connected_papers(cls, *args, **kwargs):
        raise NotImplementedError(
            'Abstract method of {} class. \
            Should be implemented in subclasses'.format(
                CitationSummarySearch.__name__ ))


    @classmethod
    def get_citation_summary(cls, **kwargs):
        limit = kwargs.get('limit')
        limit_command = ''
        if limit:
            limit_command = ' LIMIT {}'.format(limit)

        query_elements = [
            cls.query_to_match_all_connected_papers(**kwargs),
            cls.query_for_citation_summary_of_a_paper(),
            limit_command
        ]

        query = render_query(query_elements)

        response = [record for record in current_db_session.run(query)]

        def process_cited_paper(cited_paper):
            cited_paper['cited_paper_type'] = pick_one_citation_type(
                cited_paper['cited_labels']
            )
            cited_paper.pop('cited_labels')
            return cited_paper


        def process_citing_paper(citing_paper):
            citing_paper['citation_type'] = pick_one_citation_type(
                citing_paper['citing_labels']
            )
            citing_paper.pop('citing_labels')
            return citing_paper


        def process_summary_response(response_row):
            return {
                'cited_paper': process_cited_paper(
                    response_row['cited_paper']),
                'citing_papers': map(process_citing_paper,
                                     response_row['citing_papers'])
            }

        citation_summary = map(process_summary_response, response)

        # flatten the results (it has to be done on js side)
        # citation_summary = [
        #     dict(citation_row['cited_paper'], **citing_paper) \
        #     for citation_row in response \
        #     for citing_paper in citation_row['citing_papers']
        #     ]

        return citation_summary


class ConferenceRelationsSearch(CitationSummarySearch):

    @classmethod
    def query_to_match_all_connected_papers(cls, recid):
        return ''.join([
            match_record(recid, 'conference'),
            (' MATCH (conference)<-[:' + CONTRIBUTED_TO + '] '
            '-(paper)'
            ' WITH distinct paper as paper')
        ])


class InstitutionRelationsSearch(CitationSummarySearch):

    @classmethod
    def query_to_match_all_connected_papers(cls, recid):
        return ''.join([
            match_record(recid, 'institution'),
            (' MATCH (institution)<-[:' + AFFILIATED_WITH + '] '
            '-(:Author)<-[:' + AUTHORED_BY + ']-(paper)'
            ' WITH distinct paper as paper')
        ])


class ExperimentRelationsSearch(CitationSummarySearch):

    @classmethod
    def query_to_match_all_connected_papers(cls, recid):
        """
        TODO: this needs to be implemented
        reason: there's no direct connection between experiment and paper.
        Therefore it should be defined
        which papers we consider >>connected<< with experiment
        and through which relations.
        """
        raise NotImplementedError(
            'Not implemented. \
            What are the papers connected with an experiment?')


class PersonRelationsSearch(CitationSummarySearch):

    @classmethod
    def query_to_match_all_connected_papers(cls, recid):
        return ''.join([
            match_record(recid, 'person'),
            (' MATCH (person) <-[:' + WRITTEN_BY + ']-(paper)'
             ' WITH distinct paper as paper')
        ])


def produce_citation_summary(record, index):
    INDEX_TO_INDEX_SEARCH_CLASS = {
            'conferences': ConferenceRelationsSearch,
            'institutions': InstitutionRelationsSearch,
            'authors': PersonRelationsSearch
    }

    index_search_class = INDEX_TO_INDEX_SEARCH_CLASS.get(index)

    if index_search_class:
        return index_search_class.get_citation_summary(
                recid=record['control_number'])
    else:
        return None
