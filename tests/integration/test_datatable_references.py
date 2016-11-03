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


def test_references(app):
    """Tests if reference datatables work for records."""
    with app.test_client() as client:
        response = client.get('/ajax/references?recid=712925&endpoint=literature')
        assert response.status_code == 200

        response = client.get('/ajax/references?recid=1319638&endpoint=literature')
        assert response.status_code == 200

        response = client.get('/ajax/references?recid=452060&endpoint=literature')
        assert response.status_code == 200

        response = client.get('/ajax/references?recid=921978&endpoint=literature')
        assert response.status_code == 200

        response = client.get('/ajax/references?recid=1298519&endpoint=literature')
        assert response.status_code == 200
