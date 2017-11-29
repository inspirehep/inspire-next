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
from fs.opener import fsopen


RE_ALPHANUMERIC = re.compile('\W+', re.UNICODE)


class KbWriter(object):
    def __init__(self, kb_path, batch_size=1000):
        self.kb_path = kb_path
        self.data_buffer = []
        self.batch_size = batch_size

    def add_entry(self, value, kb_key):
        kb_line = self._get_kb_line(
            raw_title=value,
            kb_key=kb_key,
        )
        if kb_line:
            self._write(kb_line)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return self._close()

    def _write(self, line):
        if not line:
            return

        self.data_buffer.append(line)

        if len(self.data_buffer) >= self.batch_size:
            self._flush()

    def _flush(self):
        with fsopen(self.kb_path, mode='wb') as fd:
            fd.write(''.join(self.data_buffer))

        self.data_buffer = []

    def _close(self):
        if len(self.data_buffer):
            self._flush()

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

        result = RE_ALPHANUMERIC.sub(' ', s)
        result = ' '.join(result.split())
        result = result.upper()

        if not result:
            return

        return result
