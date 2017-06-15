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

"""INSPIRE XRootD extension."""

from __future__ import absolute_import, division, print_function

from pkg_resources import DistributionNotFound, get_distribution

try:
    # Import XRootDPyFS if available so that its
    # opener gets registered on PyFilesystem.
    get_distribution('xrootdpyfs')
    import xrootdpyfs
    XROOTD_ENABLED = True
except DistributionNotFound:
    XROOTD_ENABLED = False
    xrootdpyfs = None


class INSPIREXRootD(object):

    """INSPIRE XRootD extension."""

    def __init__(self, app=None):
        """Extension initialization."""
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Extension registration and configuration."""
        app.config['XROOTD_ENABLED'] = XROOTD_ENABLED
        if XROOTD_ENABLED:
            # Overwrite reported checksum from CERN EOS due to XRootD 3.3.6.
            app.config['XROOTD_CHECKSUM_ALGO'] = 'md5'
            app.config['FILES_REST_STORAGE_FACTORY'] = 'invenio_xrootd:eos_storage_factory'
        app.extensions['inspire-xrootd'] = self
