#
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
#

"""
INSPIRE configuration
--------------------
Instance independent configuration (e.g. which extensions to load) is defined
in ``inspire.config'' while instance dependent configuration (e.g. database
host etc.) is defined in an optional ``inspire.instance_config'' which
can be installed by a separate package.

This config module is loaded by the Flask application factory via an entry
point specified in the setup.py::

    entry_points={
        'invenio.config': [
            "inspire = inspire.config"
        ]
    },
"""

from invenio.base.config import EXTENSIONS as ORIG_EXTENSIONS

EXTENSIONS = ORIG_EXTENSIONS + [
    'inspire.ext.search_bar',
    'inspire.ext.formatter_jinja_filters'
]

CELERY_RESULT_BACKEND = "amqp://guest:guest@localhost:5672//"
BROKER_URL = "amqp://guest:guest@localhost:5672//"

SHOW_FACETS = False

try:
    from inspire.instance_config import *
except ImportError:
    pass