# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015, 2016 CERN.
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

"""DoJSON related utilities."""

from dojson import Overdo


class SchemaOverdo(Overdo):

    def __init__(self, schema=None, *args, **kwargs):
        super(SchemaOverdo, self).__init__(*args, **kwargs)
        self.schema = schema

    def do(self, blob, **kwargs):
        output = super(SchemaOverdo, self).do(blob, **kwargs)
        # output['$schema'] = self.schema FIXME Add back schema support
        return output
