# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2017 CERN.
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
"""Refextract utils."""
from __future__ import absolute_import, division, print_function

import re

import codecs
from tempfile import TemporaryFile
from fs.opener import fsopen
from inspirehep.utils.url import copy_file


RE_PUNCTUATION = re.compile(r"[\.,;'\(\)-]", re.UNICODE)


class KbWriter(object):
    def __init__(self, kb_path):
        self.kb_path = kb_path

    def add_entry(self, value, kb_key):
        kb_line = self._get_kb_line(
            raw_title=value,
            kb_key=kb_key,
        )
        if kb_line:
            self.local_file.write(kb_line)

    def __enter__(self):
        self.local_file = TemporaryFile(prefix='inspire')

        return self

    def __exit__(self, *exc):
        return self._close()

    def _close(self):
        try:
            self.local_file.seek(0)
            with fsopen(self.kb_path, mode='wb') as kb_file:
                copy_file(self.local_file, kb_file)
        finally:
            self.local_file.close()

    @classmethod
    def _get_kb_line(cls, raw_title, kb_key):
        encoded_title = None
        encode = codecs.getencoder(encoding='utf-8')
        normalized_title = cls._normalize(raw_title)
        if normalized_title:
            encoded_title, _ = encode(
                u'{}---{}\n'.format(
                    normalized_title,
                    kb_key,
                )
            )

        return encoded_title

    @staticmethod
    def _normalize(s):
        if not s:
            return

        result = RE_PUNCTUATION.sub(' ', s)
        result = ' '.join(result.split())
        result = result.upper()

        if not result:
            return

        return result
