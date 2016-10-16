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

import pytest


@pytest.yield_fixture(scope='session')
def relations_tester(app):
    from inspirehep.modules.relations import command_producers
    class NeoTester:

        def __init__(self, session):
            self._session = session

        def _get_all_results(self, cypher_query):
            results = self._session.run(cypher_query)
            return [r for r in results]

        def node_exists(self, uid, labels=None,
                        properties=None, is_exactly_same=False):
            """
            Checks whether node with given set of labels and properties exists
            and is the only one matching.
            If is_exactly_same is set, it makes sure that the found node
            doesn't have any extra labels and properties.
            """
            if not properties: properties = {}
            properties['uid'] = uid
            query = 'MATCH ' + command_producers.produce_node_block(
                    labels=labels, properties=properties, variable_name='node'
                    ) + ' RETURN node'

            results = self._get_all_results(query)

            if len(results) == 1:
                if is_exactly_same:
                    node = results[0]['node']
                    are_same_labels = set(labels) == set(node.labels)

                    return node.properties == properties and are_same_labels
                else:
                    return True
            else:
                return False

        def relation_exists(self, start_uid, relation, end_uid,
                            relation_properties=None):
            """
            Checks whether relation of certain type between two nodes exists
            and is the only one matching.

            start_inneoid -- InspireNeoID of the start node
            end_inneoid -- InspireNeoID of the end node
            relation -- type of relation
            """
            relation_string = command_producers.produce_relation_block(
                relation_type=relation, properties=relation_properties,
                variable_name='r',
                arrow_right=True)

            query = (
                'MATCH ({{uid: "{start}"}}) {relation} ({{uid: "{end}"}})'
                'RETURN count(r) AS count'
            ).format(
                start=start_uid, end=end_uid, relation=relation_string
            )
            results = self._get_all_results(query)
            return results[0]['count'] == 1


        def nodes_exist(self, uids):
            """
            Given list of nodes' InspireNeoIDs makes sure that the nodes exist.
            """

            node_blocks = [command_producers.produce_node_block(
                properties={'uid': uid}) for uid in uids]

            query = 'MATCH {} RETURN count(*) > 0 AS do_they_exist'.format(
                ', '.join(node_blocks)
            )
            results = self._get_all_results(query)
            return results[0]['do_they_exist']

    with app.app_context():
        from inspirehep.modules.relations import current_db_session
        yield NeoTester(current_db_session)


def test_journals_nodes(relations_tester):
    that = relations_tester

    assert that.node_exists('Record|^|1212905', labels=['Record', 'Journal'],
                            properties={'recid': '1212905'},
                            is_exactly_same=True)

    assert that.node_exists('Publisher|^|EDP SCIENCES', labels=['Publisher'],
                            properties={'name': 'EDP SCIENCES'},
                            is_exactly_same=True)


def test_journals_relations(relations_tester):
    that = relations_tester

    assert that.relation_exists(
            'Record|^|1212905', 'PUBLISHED_BY', 'Publisher|^|EDP SCIENCES')


def test_experiments_nodes(relations_tester):
    that = relations_tester

    assert that.node_exists('Record|^|1108642', labels=['Record', 'Experiment'],
                            properties={'recid': '1108642'},
                            is_exactly_same=True)


@pytest.mark.xfail(reason=
                   'No link between experiment and institution in demo records')
def test_experiments_relations(relations_tester):
    that = relations_tester

    assert that.relation_exists(
            'Record|^|1108642', 'AFFILIATED_WITH', 'Record|^|902725'
    )


def test_conferences_nodes(relations_tester):
    that = relations_tester

    assert that.node_exists('Record|^|1086512', labels=['Record', 'Conference'],
                            properties={'recid': '1086512'},
                            is_exactly_same=True)

    assert that.node_exists('ConferenceSeries|^|DIS',
                            labels=['ConferenceSeries'],
                            properties={'name': 'DIS'},
                            is_exactly_same=True)


def test_conferences_relations(relations_tester):
    that = relations_tester

    assert that.relation_exists(
            'Record|^|1086512', 'LOCATED_IN', 'Country|^|DE')

    assert that.relation_exists(
            'Record|^|1086512', 'IN_THE_FIELD_OF',
            'ResearchField|^|Experiment-HEP'
    )

    assert that.relation_exists(
            'Record|^|1086512', 'IN_THE_FIELD_OF',
            'ResearchField|^|Phenomenology-HEP'
    )

    assert that.relation_exists(
            'Record|^|1086512', 'IN_THE_FIELD_OF', 'ResearchField|^|Theory-HEP'
    )

    assert that.relation_exists(
            'Record|^|1086512', 'PART_OF', 'ConferenceSeries|^|DIS',
            relation_properties={'series_number': 20}
    )


def test_jobs_nodes(relations_tester):
    that = relations_tester

    assert that.node_exists('Record|^|1408251', labels=['Record', 'Job'],
                            properties={'recid': '1408251'},
                            is_exactly_same=True)


@pytest.mark.xfail(reason=
                   'No links between jobs and experiments in demo records')
def test_jobs_relations(relations_tester):
    that = relations_tester

    assert that.relation_exists(
            'Record|^|1408251', 'OFFERED_BY', 'Record|^|903369'
    )

    assert that.relation_exists(
            'Record|^|1408251', 'IN_THE_RANK_OF', 'ScientificRank|^|PHD'
    )

    assert that.relation_exists(
            'Record|^|1408251', 'IS_ABOUT_EXPERIMENT', 'Record|^|1346343'
    )

    assert that.relation_exists(
            'Record|^|1408251', 'IS_ABOUT_EXPERIMENT', 'Record|^|1332130'
    )

    assert that.relation_exists(
            'Record|^|1408251', 'IN_THE_FIELD_OF',
            'ResearchField|^|Astrophysics'
    )

    assert that.relation_exists(
            'Record|^|1408251', 'IN_THE_FIELD_OF',
            'ResearchField|^|Experiment-HEP'
    )

    assert that.relation_exists(
            'Record|^|1408251', 'IN_THE_FIELD_OF',
            'ResearchField|^|Instrumentation'
    )


def test_institutions_nodes(relations_tester):
    that = relations_tester

    assert that.node_exists('Record|^|902725',
                            labels=['Record', 'Institution'],
                            properties={'recid': '902725'},
                            is_exactly_same=True)

    assert that.node_exists('Record|^|902624',
                            labels=['Record', 'Institution'],
                            properties={'recid': '902624'},
                            is_exactly_same=True)



@pytest.mark.xfail(reason='Record no. 910724 does not exist in demo records.\
                   Should be added to make this test possible.')
def test_institutions_relations(relations_tester):
    that = relations_tester

    assert that.relation_exists('Record|^|902725',
                                'LOCATED_IN', 'Country|^|CH')

    assert that.relation_exists('Record|^|902624',
                                'LOCATED_IN', 'Country|^|DE')

    assert that.relation_exists(
            'Record|^|902624', 'CHILD_OF', 'Record|^|910724'
    )


def test_hepnames_nodes(relations_tester):
    that = relations_tester

    assert that.node_exists('Record|^|985467',
                            labels=['Record', 'Person'],
                            properties={'recid': '985467'},
                            is_exactly_same=True)

    assert that.node_exists(
            'PreviousJobPosition|^|POSTDOC|^|902725|^|1998|^|2000')


@pytest.mark.xfail(reason=
                   'Record no. 993266 is not included in demo records\
                   Even though record 985467 links to it.')
def test_hepnames_relations(relations_tester):
    that = relations_tester

    assert that.relation_exists(
            'Record|^|985467', 'SUPERVISED_BY', 'Record|^|993266',
            relation_properties={'degree_type': 'PhD'}
    )

    assert that.relation_exists(
            'Record|^|985467', 'HIRED_AS',
            'PreviousJobPosition|^|POSTDOC|^|902725|^|1998|^|2000'
    )

    assert that.relation_exists(
            'PreviousJobPosition|^|POSTDOC|^|902725|^|1998|^|2000',
            'AT', 'Record|^|902725'
    )

    assert that.relation_exists(
            'PreviousJobPosition|^|POSTDOC|^|902725|^|1998|^|2000',
            'IN_THE_RANK_OF', 'ScientificRank|^|POSTDOC'
    )


def test_literature_nodes(relations_tester):
    that = relations_tester

    assert that.node_exists(
            'Record|^|1245931',
            labels=['Record', 'Literature', 'ConferencePaper'],
            properties={
                    'recid': '1245931',
                    'title': 'Boosted Decision Trees and Applications',
                    'earliest_date': '2013'}
    )

    assert that.node_exists(
        'Record|^|692061',
        labels=['Record', 'Literature', 'Published', 'ArXiv'],
        properties={
                'recid': '692061',
                'title': 'Next-to-leading order QCD jet production with parton showers and hadronization',
                'earliest_date': '2005-09'}
    )

    assert that.node_exists(
            'Author|^|996606|^|902796',
            labels=['Author'],
            is_exactly_same=True
    )


def test_literature_relations(relations_tester):
    that = relations_tester

    assert that.relation_exists(
            'Record|^|1245931', 'CONTRIBUTED_TO', 'Record|^|1245372'
    )

    assert that.relation_exists(
            'Record|^|1245931', 'PART_OF', 'Record|^|1247304'
    )

    assert that.relation_exists(
            'Record|^|1245931', 'IN_THE_FIELD_OF',
            'ResearchField|^|Experiment-HEP'
    )

    assert that.relation_exists(
            'Record|^|1245931', 'IN_THE_FIELD_OF',
            'ResearchField|^|Math and Math Physics'
    )

    assert that.relation_exists(
            'Record|^|1245931', 'IN_THE_FIELD_OF',
            'ResearchField|^|Computing'
    )

    assert that.relation_exists(
            'Record|^|1245931', 'IN_THE_FIELD_OF',
            'ResearchField|^|Instrumentation'
    )

    assert that.relation_exists(
            'Record|^|692061', 'IN_THE_FIELD_OF',
            'ResearchField|^|Phenomenology-HEP'
    )

    assert that.relation_exists(
            'Record|^|692061', 'REFERS_TO', 'Record|^|677878'
    )

    assert that.relation_exists(
            'Record|^|692061', 'PUBLISHED_IN', 'Record|^|1214516'
    )

    assert that.relation_exists(
            'Record|^|692061', 'WRITTEN_BY', 'Record|^|996606'
    )

    assert that.relation_exists(
            'Record|^|692061', 'AUTHORED_BY', 'Author|^|996606|^|902796'
    )

    assert that.relation_exists(
            'Author|^|996606|^|902796', 'AFFILIATED_WITH', 'Record|^|902796'
    )

    assert that.relation_exists(
            'Author|^|996606|^|902796', 'REPRESENTS', 'Record|^|996606'
    )
