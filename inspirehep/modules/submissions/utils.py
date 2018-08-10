# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

import re
import requests

from flask import current_app
from inspire_dojson import marcxml2record
from inspirehep.utils.url import get_legacy_url_for_recid


def get_record_from_legacy(record_id=None):
    data = {}
    try:
        url = get_legacy_url_for_recid(record_id) + '/export/xm'
        xml = requests.get(url)
        record_regex = re.compile(
            r"\<record\>.*\<\/record\>", re.MULTILINE + re.DOTALL)
        xml_content = record_regex.search(xml.content).group()
        data = marcxml2record(xml_content)
    except requests.exceptions.RequestException:
        current_app.logger.error(
            'Failed to get record {} from legacy.'.format(record_id),
        )
    except Exception:
        current_app.logger.error(
            'Error parsing the record {} from legacy.'.format(record_id),
        )
    return data
