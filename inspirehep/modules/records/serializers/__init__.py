# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2016 CERN.
#
# INSPIRE is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Record serialization."""

from __future__ import absolute_import, print_function

from invenio_records_rest.serializers.response import search_responsify

from .impactgraph_serializer import ImpactGraphSerializer
from .json_literature import LiteratureJSONBriefSerializer
from .bibtex_serializer import BIBTEXSerializer
from .latexeu_serializer import LATEXEUSerializer
from .latexus_serializer import LATEXUSSerializer
from .cvformatlatex_serializer import CVFORMATLATEXSerializer
from .cvformathtml_serializer import CVFORMATHTMLSerializer
from .cvformattext_serializer import CVFORMATTEXTSerializer
from .schemas.json import RecordSchemaJSONBRIEFV1

from .response import record_responsify_nocache

json_literature_brief_v1 = LiteratureJSONBriefSerializer(
    RecordSchemaJSONBRIEFV1
)
json_literature_brief_v1_search = search_responsify(
    json_literature_brief_v1,
    'application/vnd+inspire.brief+json'
)


bibtex_v1 = BIBTEXSerializer()
latexeu_v1 = LATEXEUSerializer()
latexus_v1 = LATEXUSSerializer()
cvformatlatex_v1 = CVFORMATLATEXSerializer()
cvformathtml_v1 = CVFORMATHTMLSerializer()
cvformattext_v1 = CVFORMATTEXTSerializer()

bibtex_v1_response = record_responsify_nocache(
    bibtex_v1, 'application/x-bibtex')
latexeu_v1_response = record_responsify_nocache(
    latexeu_v1, 'application/x-latexeu')
latexus_v1_response = record_responsify_nocache(
    latexus_v1, 'application/x-latexus')
cvformatlatex_v1_response = record_responsify_nocache(cvformatlatex_v1,
                                                      'application/x-cvformatlatex')
cvformathtml_v1_response = record_responsify_nocache(cvformathtml_v1,
                                                     'application/x-cvformathtml')
cvformattext_v1_response = record_responsify_nocache(cvformattext_v1,
                                                     'application/x-cvformattext')

bibtex_v1_search = search_responsify(bibtex_v1, 'application/x-bibtex')
latexeu_v1_search = search_responsify(latexeu_v1, 'application/x-latexeu')
latexus_v1_search = search_responsify(latexus_v1, 'application/x-latexus')
cvformatlatex_v1_search = search_responsify(cvformatlatex_v1,
                                            'application/x-cvformatlatex')
cvformathtml_v1_search = search_responsify(cvformathtml_v1,
                                           'application/x-cvformathtml')
cvformattext_v1_search = search_responsify(cvformattext_v1,
                                           'application/x-cvformattext')
impactgraph_v1 = ImpactGraphSerializer()
impactgraph_v1_response = record_responsify_nocache(impactgraph_v1,
                                                    'application/x-impact.graph+json')
