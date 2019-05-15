# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2019 CERN.
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


# Same image inspire-next and scrapyd deployed

FROM inspirehep/inspire-next:latest

WORKDIR /usr/lib/python2.7/site-packages/hepcrawl

RUN scrapyd & sleep 10 && scrapyd-deploy local -p hepcrawl
