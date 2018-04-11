# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2018 CERN.
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

"""INSPIREHEP Celery app instantiation for tests.

This adds a simple ontology file for fast classifier runs.
"""

from __future__ import absolute_import, division, print_function

import logging
import tempfile

from flask_celeryext import create_celery_app

from .factory import create_app


HIGGS_ONTOLOGY = '''<?xml version="1.0" encoding="UTF-8" ?>

<rdf:RDF xmlns="http://www.w3.org/2004/02/skos/core#"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">

    <Concept rdf:about="http://cern.ch/thesauri/HEPontology.rdf#Higgsparticle">
        <prefLabel xml:lang="en">Higgs particle</prefLabel>
        <altLabel xml:lang="en">Higgs boson</altLabel>
        <hiddenLabel xml:lang="en">Higgses</hiddenLabel>
        <note xml:lang="en">core</note>
    </Concept>

</rdf:RDF>
'''
HIGGS_ONTOLOGY_FILE = tempfile.NamedTemporaryFile()
HIGGS_ONTOLOGY_FILE.write(HIGGS_ONTOLOGY)
HIGGS_ONTOLOGY_FILE.flush()


print('Using ontology file %s' % HIGGS_ONTOLOGY_FILE.name)
celery = create_celery_app(
    create_app(
        LOGGING_SENTRY_CELERY=True,
        HEP_ONTOLOGY_FILE=HIGGS_ONTOLOGY_FILE.name,
    )
)

# We don't want to log to Sentry backoff errors
logging.getLogger('backoff').propagate = 0
