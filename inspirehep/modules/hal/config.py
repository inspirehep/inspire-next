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

"""HAL module configuration."""

from __future__ import absolute_import, division, print_function
import flask
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

"""Filename of the base TEI template in the template environment."""
HAL_EXPORT_TEMPLATE = 'hal_tei.xml'

DEBUG = flask.current_app.debug or flask.current_app.testing

"""Collection-IRI: Identifies which collection to add records to."""
if DEBUG:
    COL_IRI = "https://api-preprod.archives-ouvertes.fr/sword/hal"
else:
    COL_IRI = "https://api.archives-ouvertes.fr/sword/hal/"

"""Edit-IRI: Identifier prefix for editing existing HAL records."""
if DEBUG:
    EDIT_IRI = "https://api-preprod.archives-ouvertes.fr/sword/"
else:
    EDIT_IRI = "https://api.archives-ouvertes.fr/sword/"

"""Ignore the certificate domain mismatch on the HAL server."""
IGNORE_CERT = True

"""Credentials for HAL SWORD API."""
HAL_USER = os.environ.get("HAL_USER")
HAL_PASSWORD = os.environ.get("HAL_PASSWORD")

"""Map between INSPIRE and HAL doctypes."""
INSPIRE_HAL_DOCTYPE_MAP = {
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
DOCTYPE_FALLBACK = "OTHER"  # Fallback: Autre publication / Other publication
