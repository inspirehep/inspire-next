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

"""Record serialization."""

from __future__ import absolute_import, division, print_function

from invenio_records_rest.serializers.response import search_responsify
from invenio_records_rest.serializers.json import JSONSerializer

from .json_literature import LiteratureJSONUISerializer
from .pybtex_serializer_base import PybtexSerializerBase
from .writers import BibtexWriter
from .schemas.base import PybtexSchema
from .schemas.json import (
    LiteratureAuthorsSchemaJSONUIV1,
    LiteratureRecordSchemaJSONUIV1,
    LiteratureReferencesSchemaJSONUIV1,
)
from .marcxml import MARCXMLSerializer
from .response import record_responsify_nocache

json_literature_ui_v1 = LiteratureJSONUISerializer(
    LiteratureRecordSchemaJSONUIV1
)
json_literature_ui_v1_search = search_responsify(
    json_literature_ui_v1,
    'application/vnd+inspire.literature.ui+json'
)
json_literature_ui_v1_response = record_responsify_nocache(
    json_literature_ui_v1,
    'application/vnd+inspire.literature.ui+json'
)

json_literature_references_v1 = JSONSerializer(
    LiteratureReferencesSchemaJSONUIV1
)
json_literature_references_v1_search = search_responsify(
    json_literature_references_v1,
    'application/json',
)
json_literature_references_v1_response = record_responsify_nocache(
    json_literature_references_v1,
    'application/json',
)

json_literature_authors_v1 = JSONSerializer(
    LiteratureAuthorsSchemaJSONUIV1
)
json_literature_authors_v1_search = search_responsify(
    json_literature_authors_v1,
    'application/json',
)
json_literature_authors_v1_response = record_responsify_nocache(
    json_literature_authors_v1,
    'application/json',
)

bibtex_v1 = PybtexSerializerBase(PybtexSchema(), BibtexWriter())
marcxml_v1 = MARCXMLSerializer()

bibtex_v1_response = record_responsify_nocache(bibtex_v1, 'application/x-bibtex')
marcxml_v1_response = record_responsify_nocache(marcxml_v1, 'application/marcxml+xml')

bibtex_v1_search = search_responsify(bibtex_v1, 'application/x-bibtex')
marcxml_v1_search = search_responsify(marcxml_v1, 'application/marcxml+xml')
