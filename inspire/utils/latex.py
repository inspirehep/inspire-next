# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
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

import re

from invenio_knowledge.api import get_kbr_keys


class MissingRequiredFieldError(LookupError):

    """Base class for exceptions in this module.
    The exception should be raised when the specific,
    required field doesn't exist in the record.
    """

    def _init_(self, field):
        self.field = field

    def _str_(self):
        return "Missing field: " + self.field


class Latex(object):
    """Class used to output LaTex format.
    TODO Fix the citation number latex
    e.g %245 citations counted in INSPIRE as of 21 Aug 2015
    """

    def __init__(self, record, latex_format):
        self.record = record
        self.arxiv_field = self._get_arxiv_field()
        self.latex_format = latex_format

    def format(self):
        """Return LaTex export for single record."""
        formats = {
            'record': self._format_record,
        }
        return formats['record']()

    def _format_record(self):
        required_fields = ['author', 'title', 'publi_info', 'arxiv']
        optional_fields = ['report_number', 'SLACcitation']
        try:
            return self._format_entry(required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_entry(self, req, opt):
        """
        :raises: MissingRequiredFieldError
        """
        out = '%\cite{' + self._get_citation_key() + '}\n'
        out += r'\bibitem{' + self._get_citation_key() + '}\n'
        out += self._fetch_fields(req, opt) + '\n'
        return out

    def _get_citation_key(self):
        """Returns citation key for LaTex"""
        if 'system_control_number' in self.record:
            result = []
            citation_key = ''
            for field in self.record['system_control_number']:
                if 'institute' in field and \
                    (field['institute'] == 'INSPIRETeX' or
                        field['institute'] == 'SPIRESTeX'):
                    result.append(field)
            for key in result:
                if key['institute'] in ('INSPIRETeX', 'SPIRESTeX'):
                    if 'system_control_number' in key:
                        citation_key = key['system_control_number']
                    elif 'value' in key:
                        citation_key = key['value']
                    elif 'obsolete' in key:
                        citation_key = key['obsolete']
                    else:
                        citation_key = ''
                if not result:
                    return ''
            if isinstance(citation_key, list):
                for element in citation_key:
                    return element.replace(' ', '')
            else:
                return citation_key.replace(' ', '')
        else:
            return ''

    def _fetch_fields(self, req_fields, opt_fields=[]):
        fields = {
            'author': self._get_author,
            'title': self._get_title,
            'publi_info': self._get_publi_info,
            'arxiv': self._get_arxiv,
            'report_number': self._get_report_number,
            'SLACcitation': self._get_slac_citation,
        }
        out = ''
        for field in req_fields:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
            # RAISE EXCEPTION HERE IF REQ FIELD IS MISSING
        for field in opt_fields:
            value = fields[field]()
            if value:
                out += self._format_output_row(field, value)
        return out

    def _format_output_row(self, field, value):
        out = ''
        if field == 'author':
            if len(value) == 1:
                out += u'  {1},\n'.format(field, value[0])
            elif len(value) > 8:
                out += u'  {1}'.format(field, value[0])
                if 'collaboration' in self.record:
                    try:
                        if 'collaboration' in self.record['collaboration'][0]:
                            collaboration = self.\
                                record['collaboration'][0]['collaboration']
                            if 'Collaboration' in collaboration:
                                out += u' {{\it et al.}} [' + collaboration + '],\n'
                            else:
                                out += u' {{\it et al.}} [' + collaboration + ' Collaboration],\n'
                    except IndexError:
                        pass
                else:
                    out += u' {\it et al.},\n'
            else:
                out += u'  {} and {},\n'.format(', '.join(value[:-1]),
                                                value[-1])
        elif field == 'title':
            out += u'  {1}\n'.format(field, value)
        elif field == 'publi_info':
            out += u'  {1}.\n'.format(field, value)
        elif field == 'arxiv':
            if self._get_publi_info():
                out += u'  [{1}].\n'.format(field, value)
            else:
                out += u'  {1}.\n'.format(field, value)
        elif field == 'report_number':
            out += u'  {1}.\n'.format(field, value)
        elif field == 'SLACcitation':
            out += u'  {1}'.format(field, value)
        return out

    def _get_arxiv_field(self):
        """Return arXiv field if exists"""
        if 'report_number' in self.record:
            for field in self.record['report_number']:
                if ('source' in field and field['source'] == 'arXiv') \
                    or 'arxiv_category' in field or \
                    ('primary' in field and
                        field['primary'].upper().startswith('ARXIV:')):
                    return field

    def _get_author(self):
        """Return list of name(s) of the author(s)."""
        re_last_first = re.compile(
            r'^(?P<last>[^,]+)\s*,\s*(?P<first_names>[^\,]*)(?P<extension>\,?.*)$'
        )
        re_initials = re.compile(r'(?P<initial>\w)([\w`\']+)?.?\s*')
        re_tildehyph = re.compile(
            ur'(?<=\.)~(?P<hyphen>[\u002D\u00AD\u2010-\u2014-])(?=\w)'
        )
        result = []
        if 'authors' in self.record:
            for author in self.record['authors']:
                if author['full_name']:
                    if isinstance(author['full_name'], list):
                        author_full_name = ' '.join(full_name for full_name
                                                    in author['full_name'])
                        first_last_match = re_last_first.search(
                            author_full_name)
                        if first_last_match:
                            first = re_initials.sub(
                                r'\g<initial>.~',
                                first_last_match.group('first_names')
                            )
                            first = re_tildehyph.sub(r'\g<hyphen>', first)
                            result.append(first +
                                          first_last_match.group('last') +
                                          first_last_match.group('extension'))
                    else:
                        first_last_match = re_last_first.search(
                            author['full_name'])
                        if first_last_match:
                            first = re_initials.sub(
                                r'\g<initial>.~',
                                first_last_match.group('first_names')
                            )
                            first = re_tildehyph.sub(r'\g<hyphen>', first)
                            result.append(first +
                                          first_last_match.group('last') +
                                          first_last_match.group('extension'))
        elif 'corporate_author' in self.record:
            if isinstance(self.record['corporate_author'], list):
                for corp_author in self.record['corporate_author']:
                    if 'corporate_author' in corp_author:
                        first_last_match = re_last_first.search(
                            corp_author['corporate_author'])
                        if first_last_match:
                            first = re_initials.sub(
                                r'\g<initial>.~',
                                first_last_match.group('first_names')
                            )
                            first = re_tildehyph.sub(r'\g<hyphen>', first)
                            result.append(first +
                                          first_last_match.group('last') +
                                          first_last_match.group('extension'))
            else:
                first_last_match = re_last_first.search(
                    self.record['corporate_author']['corporate_author']
                )
                if first_last_match:
                    first = re_initials.sub(
                        r'\g<initial>.~',
                        first_last_match.group('first_names')
                    )
                    first = re_tildehyph.sub(r'\g<hyphen>', first)
                    result.append(first +
                                  first_last_match.group('last') +
                                  first_last_match.group('extension'))
        return result

    def _get_title(self):
        """Return record titles"""
        record_title = ''
        if 'title' in self.record:
            if isinstance(self.record['title'], list):
                for title in self.record['title']:
                    if 'title' in title:
                        record_title = title['title']
                        break
            else:
                record_title = self.record['title']['title'].strip()
            return "%``" + re.sub(r'(?<!\\)([#&%])', r'\\\1', record_title) \
                         + ",''"
        else:
            return record_title

    def _get_publi_info(self):
        if 'publication_info' in self.record:
            journal_title, journal_volume, year, journal_issue, pages = \
                ('', '', '', '', '')
            for field in self.record['publication_info']:
                out = ''
                if 'journal_title' in field:
                    if isinstance(field['journal_title'], list):
                        journal_title = field['journal_title'][-1].\
                            replace(".", '.\\ ')
                    else:
                        journal_title = field['journal_title'].\
                            replace(".", '.\\ ')
                    if 'journal_volume' in field and not \
                            field['journal_title'] == 'Conf.Proc.':
                        journal_letter = ''
                        char_i = 0
                        for char in field['journal_volume']:
                            if char.isalpha():
                                char_i += 1
                            else:
                                break
                        journal_letter = field['journal_volume'][:char_i]
                        if journal_letter and journal_title != ' ':
                            journal_letter = ' ' + journal_letter
                        journal_volume = journal_letter + ' {\\bf ' + \
                            field['journal_volume'][char_i:] + '}'
                    if 'year' in field:
                        if isinstance(field['year'], list):
                            year = ' (' + field['year'][-1] + ')'
                        else:
                            year = ' (' + field['year'] + ')'
                    if 'journal_issue' in field:
                        if field['journal_issue']:
                            if self.latex_format == 'latex_eu':
                                journal_issue = ' ' + \
                                                field['journal_issue'] + ', '
                            else:
                                journal_issue = ', no. ' + \
                                                field['journal_issue']
                    if 'page_artid' in field:
                        page_artid = ''
                        if field['page_artid']:
                            if isinstance(field['page_artid'], list):
                                    dashpos = field['page_artid'][-1].find('-')
                                    if dashpos > -1:
                                        page_artid = field['page_artid'][-1][:dashpos]
                                    else:
                                        page_artid = field['page_artid'][-1]
                            else:
                                dashpos = field['page_artid'].find('-')
                                if dashpos > -1:
                                    page_artid = field['page_artid'][:dashpos]
                                else:
                                    page_artid = field['page_artid']
                            if self.latex_format == 'latex_eu':
                                pages = ' ' + page_artid
                            else:
                                pages = ', ' + page_artid
                    break
                else:
                    if 'pubinfo_freetext' in field and len(field) == 1:
                        return field['pubinfo_freetext']
            if self.latex_format == 'latex_eu':
                out += journal_title + journal_volume + year + \
                    journal_issue + pages
            else:
                out += journal_title + journal_volume + journal_issue + \
                    pages + year
            if out:
                return out

    def _get_arxiv(self):
        arxiv = ''
        if self.arxiv_field:
            if 'primary' in self.arxiv_field:
                arxiv = self.arxiv_field['primary']
                if 'arxiv_category' in self.arxiv_field:
                    arxiv += ' [' + self.arxiv_field['arxiv_category'] + ']'
        return arxiv

    def _get_report_number(self):
        """Return report number separated by commas"""
        if not (self._get_publi_info() or self._get_arxiv()):
            report_number = []
            if 'report_number' in self.record:
                for field in self.record['report_number']:
                    if len(field) == 1:
                        report_number.append(field['primary'])
                return ', '.join(str(p) for p in report_number)
            else:
                return report_number

    def _get_slac_citation(self):
        """Return SLACcitation"""
        cite_line = ''
        cite_element = ''
        if self.arxiv_field:
            if 'primary' in self.arxiv_field:
                cite_element = self.arxiv_field['primary'].upper()
                cite_line = '%%CITATION = ' + \
                            cite_element + ';%%'
        elif self._get_pubnote():
            cite_element = self._get_pubnote()
            cite_line = '%%CITATION = ' + cite_element + ';%%'
        elif 'report_number' in self.record:
            if isinstance(self.record['report_number'], list):
                for field in self.record['report_number']:
                    if 'arxiv_category' in field:
                        cite_element = field['primary'].upper()
                        cite_line = '%%CITATION = ' + cite_element + ';%%'
                if not cite_element:
                    cite_element = self.record['report_number'][0]['primary'].upper()
                    cite_line = '%%CITATION = ' + cite_element + ';%%'
        else:
            cite_element = str(self.record['recid'])
            cite_line = '%%CITATION = ' + 'INSPIRE-' + \
                cite_element + ';%%'
        return cite_line

    def _get_pubnote(self):
        """Return publication note"""
        journal, volume, pages = ['', '', '']
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            if isinstance(pub_info, list):
                for field in pub_info:
                    if 'journal_title' in field:
                        journal = field['journal_title']
                    if 'journal_volume' in field:
                        volume = field['journal_volume']
                    if 'page_artid' in field:
                        pages = field['page_artid']
                        if pages:
                            if isinstance(pages, list):
                                for page in pages:
                                    dashpos = page.find('-')
                                    break
                            else:
                                dashpos = pages.find('-')
                            if dashpos > -1:
                                pages = pages[:dashpos]
                    try:
                        if journal and (volume != '' or pages != ''):
                            coden = ','.join(
                                [get_kbr_keys("CODENS", searchvalue=journal,
                                 searchtype='e')[0][0],
                                 volume, pages])
                            return coden
                    except:
                        return ''
            else:
                if 'journal_title' in pub_info:
                    journal = pub_info['journal_title']
                if 'journal_volume' in pub_info:
                    volume = pub_info['journal_volume']
                if 'page_artid' in pub_info:
                    pages = pub_info['page_artid']
                    if pages:
                        dashpos = pages.find('-')
                        if dashpos > -1:
                            pages = pages[:dashpos]
                try:
                    if journal and (volume != '' or pages != ''):
                        coden = ','.join(
                            [get_kbr_keys("CODENS", searchvalue=journal,
                             searchtype='e')[0][0],
                             volume, pages])
                        return coden
                except:
                    return ''
        else:
            return ''
