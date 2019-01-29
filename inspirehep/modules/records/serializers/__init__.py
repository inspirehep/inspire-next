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

from .json_literature import (
    LiteratureCitationsJSONSerializer,
    LiteratureJSONUISerializer,
    FacetsJSONUISerializer
)
from .pybtex_serializer_base import PybtexSerializerBase
from .writers import BibtexWriter
from .schemas.base import PybtexSchema
from .schemas.latex import LatexSchema
from .schemas.json import (
    LiteratureAuthorsSchemaJSONUIV1,
    LiteratureRecordSchemaJSONUIV1,
    LiteratureReferencesSchemaJSONUIV1,
    CitationItemSchemaV1,
    AuthorsRecordSchemaJSONUIV1,
    UIDisplayLiteratureRecordJsonUIV1,
)
from .marcxml import MARCXMLSerializer
from .latex import LatexSerializer
from .response import record_responsify_nocache, facets_responsify

json_literature_ui_v1 = LiteratureJSONUISerializer(
    LiteratureRecordSchemaJSONUIV1
)

json_literature_ui_v1_search = LiteratureJSONUISerializer(
    UIDisplayLiteratureRecordJsonUIV1
)

json_literature_ui_v1_search = search_responsify(
    json_literature_ui_v1_search,
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

json_literature_citations_v1 = LiteratureCitationsJSONSerializer(
    CitationItemSchemaV1
)
json_literature_citations_v1_response = record_responsify_nocache(
    json_literature_citations_v1,
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

json_literature_aggregations_ui_v1 = FacetsJSONUISerializer(
    json_literature_ui_v1
)

json_literature_search_aggregations_ui_v1 = facets_responsify(
    json_literature_aggregations_ui_v1,
    'application/json',
)

json_authors_ui_v1 = JSONSerializer(
    AuthorsRecordSchemaJSONUIV1
)

json_authors_ui_v1_search = search_responsify(
    json_authors_ui_v1,
    'application/vnd+inspire.literature.ui+json'
)

json_authors_ui_v1_response = record_responsify_nocache(
    json_authors_ui_v1,
    'application/vnd+inspire.literature.ui+json'
)

bibtex_v1 = PybtexSerializerBase(PybtexSchema(), BibtexWriter())
marcxml_v1 = MARCXMLSerializer()
latex_v1_EU = LatexSerializer('EU', schema_class=LatexSchema)
latex_v1_US = LatexSerializer('US', schema_class=LatexSchema)

bibtex_v1_response = record_responsify_nocache(bibtex_v1,
                                               'application/x-bibtex')
latex_v1_response_eu = record_responsify_nocache(latex_v1_EU,
                                                 'application/vnd.eu+x-latex')
latex_v1_response_us = record_responsify_nocache(latex_v1_US,
                                                 'application/vnd.us+x-latex')
marcxml_v1_response = record_responsify_nocache(marcxml_v1,
                                                'application/marcxml+xml')

bibtex_v1_search = search_responsify(bibtex_v1, 'application/x-bibtex')
marcxml_v1_search = search_responsify(marcxml_v1, 'application/marcxml+xml')
latex_v1_search_eu = search_responsify(latex_v1_EU, 'application/vnd.eu+x-latex')
latex_v1_search_us = search_responsify(latex_v1_US, 'application/vnd.us+x-latex')
