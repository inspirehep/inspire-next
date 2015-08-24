# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014, 2015 CERN.
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

from invenio.base.config import CFG_DATADIR, CFG_SITE_URL

CFG_ROBOTUPLOAD_SUBMISSION_BASEURL = CFG_SITE_URL
WORKFLOWS_MATCH_REMOTE_SERVER_URL = "{0}/search".format(CFG_SITE_URL)
PENDING_RECORDS_CACHE_TIMEOUT = 2629743  # one month
WORKFLOWS_STORAGEDIR = os.path.join(CFG_DATADIR, "workflows", "storage")
