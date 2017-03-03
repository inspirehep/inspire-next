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

from __future__ import absolute_import, division, print_function

import time

from inspirehep.utils.record_getter import get_es_record


class MissingRequiredFieldError(LookupError):

    """Base class for exceptions in this module.
    The exception should be raised when the specific,
    required field doesn't exist in the record.
    """

    def __init__(self, field):
        self.field = field

    def __str__(self):
        return "Missing field: " + self.field


class Export(object):
    """Base class used for export formats."""

    def __init__(self, record, *args, **kwargs):
        self.record = record

    def _get_citation_key(self):
        """Returns citation keys."""
        result = []
        citation_key = ''
        if 'external_system_numbers' in self.record:
            for field in self.record['external_system_numbers']:
                if 'institute' in field and \
                    (field['institute'] == 'INSPIRETeX' or
                        field['institute'] == 'SPIRESTeX'):
                    result.append(field)
            for key in result:
                if key['institute'] in ('INSPIRETeX', 'SPIRESTeX'):
                    if 'value' in key:
                        citation_key = key['value']
        if isinstance(citation_key, list):
            return citation_key[0].replace(' ', '')
        else:
            return citation_key.replace(' ', '')

    def _get_doi(self):
        """Return doi"""
        if 'dois' in self.record:
            doi_list = []
            for doi in self.record['dois']:
                doi_list.append(doi['value'])
            return ', '.join(doi for doi in list(set(doi_list)))
        else:
            return ''

    @property
    def arxiv_field(self):
        """Return arXiv field if exists"""
        if 'arxiv_eprints' in self.record:
            for field in self.record['arxiv_eprints']:
                return field

    def _get_arxiv(self):
        """Return arXiv and arXiv category"""
        arxiv = ''
        if self.arxiv_field:
            if 'value' in self.arxiv_field:
                arxiv = self.arxiv_field['value']
                if self.arxiv_field.get('categories', []):
                    arxiv += ' ['
                    arxiv += ",".join(self.arxiv_field.get('categories', []))
                    arxiv += ']'
        return arxiv

    def _get_report_number(self):
        """Return report number separated by commas"""
        report_number = []
        if 'report_numbers' in self.record:
            for field in self.record['report_numbers']:
                if 'value' in field:
                    report_number.append(field['value'])
            return ', '.join(str(p) for p in report_number)
        else:
            return report_number

    def _get_slac_citation(self):
        """Return SLACcitation"""
        cite_line = ''
        cite_element = ''
        if self.arxiv_field:
            if 'value' in self.arxiv_field:
                cite_element = self.arxiv_field['value'].upper()
                cite_line = '%%CITATION = ' + \
                            cite_element + ';%%'
        elif self._get_pubnote():
            cite_element = self._get_pubnote()
            cite_line = '%%CITATION = ' + cite_element + ';%%'
        elif 'report_numbers' in self.record:
            for field in self.record.get('arxiv_eprints', []):
                if 'categories' in field:
                    cite_element = field['value'].upper()
                    cite_line = '%%CITATION = ' + cite_element + ';%%'
            if not cite_element and self.record['report_numbers']:
                cite_element = self.record[
                    'report_numbers'][0]['value'].upper()
                cite_line = '%%CITATION = ' + cite_element + ';%%'
        else:
            cite_element = str(self.record['control_number'])
            cite_line = '%%CITATION = ' + 'INSPIRE-' + \
                cite_element + ';%%'
        return cite_line

    def _get_citation_number(self):
        """Returns how many times record was cited. If 0, returns nothing"""
        today = time.strftime("%d %b %Y")
        record = get_es_record('lit', self.record['control_number'])
        citations = ''
        try:
            times_cited = record['citation_count']
            if times_cited != 0:
                if times_cited > 1:
                    citations = '%d citations counted in INSPIRE as of %s' \
                                % (times_cited, today)
                else:
                    citations = '%d citation counted in INSPIRE as of %s'\
                                % (times_cited, today)
        except KeyError:
            pass
        return citations
