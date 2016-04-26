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


def test_citations(app):
    """Tests if citation datatables work for records."""
    with app.test_client() as client:
        response = client.get('/ajax/citations?recid=712925&collection=literature')
        assert response.status_code == 200

        response = client.get('/ajax/citations?recid=1319638&collection=literature')
        assert response.status_code == 200

        response = client.get('/ajax/citations?recid=452060&collection=literature')
        assert response.status_code == 200

        response = client.get('/ajax/citations?recid=921978&collection=literature')
        assert response.status_code == 200

        response = client.get('/ajax/citations?recid=1298519&collection=literature')
        assert response.status_code == 200
