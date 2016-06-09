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


def test_other_conferences(app):
    """Tests if citation datatables work for records."""
    with app.test_client() as client:
        response = client.get('/ajax/conferences/series?recid=1331207&seriesname=Rencontres%20de%20Moriond')
        assert response.status_code == 200

        response = client.get('/ajax/conferences/series?recid=1346335&seriesname=EDS')
        assert response.status_code == 200

        response = client.get('/ajax/conferences/series?recid=1320036&seriesname=Quarks')
        assert response.status_code == 200

        response = client.get('/ajax/conferences/series?recid=976391&seriesname=LCWS')
        assert response.status_code == 200

        response = client.get('/ajax/conferences/series?recid=977661&seriesname=NSS')
        assert response.status_code == 200
