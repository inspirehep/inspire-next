# -*- coding: utf-8 -*-
##
## This file is part of INSPIRE.
## Copyright (C) 2014 CERN.
##
## INSPIRE is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## INSPIRE is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Authors module.

This module is work in progress. To enable it, remove the entry from
PACKAGE_EXCLUDED in invenio.base.config.
"""

from warnings import warn

# TODO Remove this warning when authors module is stable.
warn("This module is 'work in progress' and thus unstable.", ImportWarning)

# TODO
# Frontend
#
# + replace flot with more reliable library (bundles.py and js files)
# + plug-in views.py to the records after relationships are ready
# + add links on the profile page
#   - profilecoauthors.js
#   - profilekeywords.js
#   - profilestats.js
#   -
#
# + make internationalization work
#   - check the console for "translated to undefined"
#     there are two sources of this: statstable.mustache and profiletoggle.js
#
# Backend
#
# + implement querying the search engine in pubslist.js (getIdsFromToggles)
