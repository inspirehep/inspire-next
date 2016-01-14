# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
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

from flask_cache import make_template_fragment_key

from inspirehep.ext.cache_manager.cache import inspire_cache

from inspirehep.modules.citations.tasks import update_citation_count_for_records

from invenio.testsuite import InvenioTestCase


class CacheManagerTest(InvenioTestCase):

    def cache_record_oneline_views(self):
        from invenio_ext.template import render_template_to_string

        for record in self.records:
            render_template_to_string("citations.html", record=record, reference=None)

    def cache_record_brief_search_views(self):
        for recid in self.recids:
            self.client.get("/search?cc=HEP&&p=control_number:{recid}".format(recid=str(recid)))

    def check_if_record_oneline_view_cached(self, recid):
        redis_key = make_template_fragment_key('record_oneline', vary_on=[str(recid)])
        return inspire_cache.cache.get(redis_key) is not None

    def check_if_record_brief_search_cached(self, recid):
        redis_key = make_template_fragment_key('record_brief', vary_on=[str(recid)])
        return inspire_cache.cache.get(redis_key) is not None

    def setUp(self):
        import copy
        from invenio_records.api import get_record
        from invenio_search.api import Query
        import time
        # SCENARIO:
        # in this test we update record no. 1196797 changing its title and altering references
        # (we remove one reference and add the other one)
        #
        # LINKS BEFORE TEST:
        # 1291940 ---> 1196797 ---> 454197 <---1328493  1325552 ---> 1293923 ---> 955176
        #
        # LINKS AFTER TEST:
        # 1291940 ---> 1196797 ---> 1293923 ---> 9551761   1325552 ---> 1293923    1328493 ---> 454197
        #
        # (A ---> B means that A refers to B)
        #
        # All 7 records should have cached before update of record 1196797 2 different types of views:
        # record_oneline view and record_brief view.
        # After the update they should have cached views according to the schema below:

        self.expected_views_caching_after_update = {
            '1196797': {
                'record_oneline': False,
                'record_brief_search': False
            },
            '1291940': {
                'record_oneline': True,
                'record_brief_search': True
            },
            '1328493': {
                'record_oneline': True,
                'record_brief_search': True
            },
            '454197': {
                'record_oneline': True,
                'record_brief_search': False
            },
            '1293923': {
                'record_oneline': True,
                'record_brief_search': False
            },
            '955176': {
                'record_oneline': True,
                'record_brief_search': True
            },
            '1325552':
                {
                'record_oneline': True,
                'record_brief_search': True
            }
        }

        self.recids = [1196797, 1291940, 1328493, 454197, 1293923, 955176, 1325552]
        self.records = Query(' or '.join(['control_number:' + str(recid) for recid in self.recids])).search().records()
        self.cache_record_brief_search_views()
        self.cache_record_oneline_views()
        self.changed_record_id = u'1196797'
        self.removed_reference = u'454197'
        self.added_reference = u'1293923'

        record = get_record(self.changed_record_id)
        self.old_title = copy.deepcopy(record['titles'][0]['title'])
        self.old_references = copy.deepcopy(record['references'])

        # change record's title
        record['titles'][0]['title'] = u'Les Vacances du petit Nicolas'

        # change record's references - stop referring to 454197, start - to 1293923
        for ref in record['references']:
            if ref.get('recid'):
                if int(ref['recid']) == int(self.removed_reference):
                    ref['recid'] = int(self.added_reference)

        # commit changes
        record.commit()

        # wait few seconds to make sure InspireCacheManager has already done its job
        time.sleep(10)

    def tearDown(self):
        from invenio_records.api import get_record
        from invenio_search.api import Query
        import time

        # clear cache
        inspire_cache.clear()

        # undo changes in the record
        record = get_record(self.changed_record_id)
        record['references'] = self.old_references
        record['titles'][0]['title'] = self.old_title
        record.commit()

        # make sure changes have been applied to ES and all citation_counts have been recalculated
        timeout = 15  # [seconds]
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            es_record = Query('control_number:' + self.changed_record_id).search().records().pop()
            references = [unicode(ref['recid']) for ref in es_record['references'] if ref.get('recid')]
            title = es_record['titles'][0]['title']

            if self.removed_reference in references \
                    and self.added_reference not in references \
                    and title == self.old_title:
                break
            else:
                time.sleep(1)

        update_citation_count_for_records.delay([int(self.removed_reference), int(self.added_reference)])

        # make sure citation_counts have been updated
        time.sleep(4)

    def test_cache_management(self):
        self.views_caching_after_update = {
            str(recid):
                {
                'record_oneline': self.check_if_record_oneline_view_cached(recid),
                'record_brief_search': self.check_if_record_brief_search_cached(recid)
            }
            for recid in self.recids
        }
        differences = []
        for recid in self.expected_views_caching_after_update:
            recids_views = self.views_caching_after_update.get(recid)
            if recids_views:
                for view in ['record_oneline', 'record_brief_search']:
                    was_cached = recids_views.get(view)
                    if was_cached != self.expected_views_caching_after_update[recid][view]:
                        differences.append((recid, view, was_cached))
            else:
                differences.append((recid, 'all'))

        self.failIf(differences)
