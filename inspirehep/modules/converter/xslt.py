# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Wrapper for an XSLT engine."""

from __future__ import print_function, absolute_import

import os
import lxml.etree as ET


def convert(xml, xslt_filename):
    """Convert XML using given XSLT stylesheet."""
    if not os.path.isabs(xslt_filename):
        prefix_dir = os.path.dirname(os.path.realpath(__file__))
        xslt_filename = os.path.join(prefix_dir, "stylesheets", xslt_filename)

    dom = ET.fromstring(xml)
    xslt = ET.parse(xslt_filename)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    return ET.tostring(newdom, pretty_print=False)
