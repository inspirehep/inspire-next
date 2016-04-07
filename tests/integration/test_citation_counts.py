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

from inspirehep.utils.record_getter import get_es_record


def test_citation_counts_are_correct(app):
    def get_citation_count(recid):
        record = get_es_record('literature', recid)
        citation_count = record['citation_count']

        return citation_count

    with app.app_context():
        assert get_citation_count(712925) == 97
        assert get_citation_count(12291) == 12
        assert get_citation_count(1319638) == 8
        assert get_citation_count(452060) == 6
        assert get_citation_count(921978) == 5
        assert get_citation_count(1298519) == 3
        assert get_citation_count(1298029) == 3
        assert get_citation_count(1391029) == 2
        assert get_citation_count(686477) == 2
        assert get_citation_count(450836) == 1
        assert get_citation_count(611633) == 1
        assert get_citation_count(1345828) == 1
