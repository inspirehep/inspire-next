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

from pybtex.database.output.bibtex import Writer

from ..config import MAX_AUTHORS_BEFORE_ET_AL


class BibtexWriter(Writer):
    """Formats bibtex, but limits total number of authors displayed."""

    def _write_persons(self, stream, persons, role):
        """Format and write ``persons`` to ``stream``.

        Args:
            stream (file): stream BibTeX should be written to
            persons (list of pybtex.database.Person): list of people to create a citation with
            role (string): role common to the group of people being written (e.g. 'author').
                Synonymous to the BibTeX field the persons should be put into.

        Note:
            Overrides ``pybtex.database.output.bibtex.Writer``.

        """
        if len(persons) > MAX_AUTHORS_BEFORE_ET_AL:
            self._write_field(stream, role, self._format_name(stream, persons[0]) + " and others")
        else:
            super(BibtexWriter, self)._write_persons(stream, persons, role)
