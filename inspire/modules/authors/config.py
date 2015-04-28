# -*- coding: utf-8 -*-
## This file is part of INSPIRE.
## Copyright (C) 2014, 2015 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

""" Configuration of authors module."""

from invenio.config import CFG_SITE_URL

# Record definition variables

AUTHORS_IDENTIFIERS_TYPES = ['authorid', 'orcid', 'arxiv']

AUTHORS_AFFILIATION_STATUS = ['current']
AUTHORS_EXPERIMENT_STATUS = ['current']
AUTHORS_EMAIL_STATUS = ['current']

AUTHORS_NAME_NUMERATIONS = "^Jr\.|Sr\.|I{1,3}|IV|VI{0,3}$"
AUTHORS_NAME_STATUSES = ['active', 'deceased', 'departed', 'retired']
AUTHORS_NAME_TITLES = ['Sir']

AUTHORS_AFFILIATION_RANKS = ['senior', 'junior', 'staff', 'visitor', 'postdoc',
                             'phd', 'masters', 'undergrad']

# Author new/update form

AUTHORS_UPDATE_BASE_URL = CFG_SITE_URL
""" URL used to prefill author update form """
