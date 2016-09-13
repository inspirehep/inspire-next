# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this licence, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

from __future__ import absolute_import, division, print_function

hal_doctype = {
    'conferencepaper': "COMM",
    # Communication dans un congrès / Conference communication
    'thesis': "THESE",
    # Thèse / Thesis
    'proceedings': "DOUV",
    # Direction d'ouvrage, Proceedings / Directions of work, Proceedings
    'book': "OUV",
    # Ouvrage (y compris édition critique et traduction) /
    # Book (includes scholarly edition and translation)
    'bookchapter': "COUV",
    # Chapitre d'ouvrage / Book chapter
    # 'review': "NOTE",
    # Note de lecture / Book review
    'published': "ART",
    # Article dans une revue / Journal article
    'lectures': "LECTURE",
    # Cours / Course
}
doctype_fallback = "OTHER"  # Fallback: Autre publication / Other publication
