# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

import os

import time

from collections import Counter

from inspirehep.dojson.processors import convert_marcxml

from inspirehep.modules.citations.tasks import update_citation_count_for_records

from invenio.testsuite import InvenioTestCase, make_test_suite, run_test_suite

from invenio_ext.sqlalchemy import db

from invenio_search.api import Query

import pkg_resources


class CitationCountTest(InvenioTestCase):

    def test_citation_count(self):
        from invenio_ext.es import es
        from invenio_search.api import Query
        recid = u'1196797'
        count = len(Query('refersto:'+recid).search())
        record = es.get(index='hep', id=recid)
        self.assertEqual(count, record['_source'].get('citation_count'))


class CitationTestsOnRecordInsert(InvenioTestCase):

    def setUp(self):

        from invenio_records.api import create_record
        from invenio_records.models import Record
        self.marcxml_file = pkg_resources.resource_stream('tests',
                                                          os.path.join(
                                                              'fixtures',
                                                              'test_citation_counts.xml')
                                                          )

        self.converted_record = convert_marcxml(self.marcxml_file).next()
        self._transaction = db.session.begin_nested()
        self.cited_recids = [r['recid'] for r in self.converted_record['references'] if r.get('recid')]
        self.new_recid = self.converted_record['control_number']
        self.expected_citation_counts_after_insert = Counter()
        self.citation_counts_after_insert = Counter()

        for cited_recid in self.cited_recids:
            references_to_cited_recid = [r['recid']
                                         for r in Query('refersto:' + str(cited_recid)).search().records()
                                         if r.get('recid')]
            queried_records = Query('control_number:' + str(cited_recid)).search().records()
            cited_record = queried_records[0] if queried_records else None

            if cited_record:
                if int(self.new_recid) in references_to_cited_recid:
                    self.expected_citation_counts_after_insert[cited_recid] = cited_record.get('citation_count', 0)
                else:
                    self.expected_citation_counts_after_insert[cited_recid] = \
                        cited_record.get('citation_count', 0) + 1

        self.record = Record(id=self.new_recid)
        db.session.add(self.record)
        create_record(self.converted_record)

        # we need to make sure the new record has been already indexed
        timeout = 15  # [seconds]
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            if len(Query('control_number:' + self.new_recid).search()) > 0:
                break
            else:
                time.sleep(1)

        # wait a few seconds to make sure that the field citation_count of cited records have been updated
        time.sleep(6)

    def tearDown(self):
        from invenio_ext.es import es
        self._transaction.rollback()
        es.delete(index='hep', doc_type='record', id=self.new_recid)

        # we need to make sure the new record has been deleted from elasticsearch
        timeout = 15  # [seconds]
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            if len(Query('control_number:' + self.new_recid).search()) == 0:
                break
            else:
                time.sleep(1)
        update_citation_count_for_records.delay(self.expected_citation_counts_after_insert.keys())

    def test_citation_count_after_insert(self):

        for key in self.expected_citation_counts_after_insert:
            updated_cited_record = Query('control_number:' + str(key)).search().records()[0]
            self.citation_counts_after_insert[key] = updated_cited_record.get('citation_count')
        self.assertEqual(self.expected_citation_counts_after_insert, self.citation_counts_after_insert)


class CitationTestsOnRecordUpdate(InvenioTestCase):

    def setUp(self):
        from invenio_records.api import get_record
        from invenio_search.api import Query
        import copy

        self.test_recid = u'1196797'
        record = get_record(recid=self.test_recid)
        self.removed_reference_recid = u'454197'
        self.citation_count_before_update = Query('control_number:' + str(self.removed_reference_recid))\
            .search().records()[0]['citation_count']

        self.expected_citation_count_after_update = self.citation_count_before_update - 1
        self.references_before_update = copy.deepcopy(record['references'])

        # remove a reference
        reference_to_remove = [ref for ref in record['references']
                               if ref.get('recid') and ref['recid'] == self.removed_reference_recid].pop()
        record['references'].remove(reference_to_remove)
        record.commit()

        # we need to make sure the record has been already updated also in es
        timeout = 15  # [seconds]
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            es_record = Query('control_number:' + self.test_recid).search().records()[0]
            references = [ref['recid'] for ref in es_record['references'] if ref.get('recid')]

            if self.removed_reference_recid not in references:
                break
            else:
                time.sleep(1)

        # wait a few seconds to make sure that the field citation_count of removed reference has been updated
        time.sleep(6)

    def test_citation_count_on_update(self):
        updated_citation_count = Query('control_number:' +
                                       str(self.removed_reference_recid)).search().records()[0]['citation_count']
        self.assertEqual(updated_citation_count, self.expected_citation_count_after_update)

    def tearDown(self):
        from invenio_search.api import Query
        from invenio_records.api import get_record

        record = get_record(recid=self.test_recid)
        record['references'] = self.references_before_update
        record.commit()

        # we need to make sure the record has been already restored to initial state also in es
        timeout = 15  # [seconds]
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            es_record = Query('control_number:' + self.test_recid).search().records().pop()
            references = [ref['recid'] for ref in es_record['references'] if ref.get('recid')]

            if self.removed_reference_recid in references:
                break
            else:
                time.sleep(1)

        update_citation_count_for_records.delay([self.removed_reference_recid])


TEST_SUITE = make_test_suite(CitationCountTest, CitationTestsOnRecordInsert, CitationTestsOnRecordUpdate)

if __name__ == "__main__":
    run_test_suite(TEST_SUITE)
