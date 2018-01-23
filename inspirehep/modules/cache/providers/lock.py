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

"""Cache for marking a record as locked."""

from __future__ import absolute_import, division, print_function

from invenio_cache import current_cache


class LockCache(object):
    """Lock cache for ``pid_value``"""

    key_prefix = 'lock::'

    def __init__(self):
        """Initialize the cache."""

    def _prefix(self, key):
        """Set prefix to a key.

        Args:
            key (str): a key name.

        Returns:
            str: a key with the ``key_prefix`` prefix.
        """
        return '{0}{1}'.format(self.key_prefix, key)

    def get(self, key):
        """Get the key value.

        Args:
            key (str): a key name.

        Returns:
            str: the value of the given key.
        """
        return current_cache.get(self._prefix(key))

    def set(self, key, value, timeout=7200):
        """Set the key and value.

        Args:
            key (str): a key name.
            value (str): a value.
            timeout (int): a timeout time in seconds.

        Returns:
            bool: if the key is stored.
        """
        return current_cache.set(
            self._prefix(key), value, timeout=timeout)

    def delete(self, key):
        """Delete the key.

        Args:
            key (str): a key name.

        Returns:
            bool: if the key is deleted.
        """
        return current_cache.delete(self._prefix(key))
