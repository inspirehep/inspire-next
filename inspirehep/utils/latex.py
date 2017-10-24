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

import re

from inspirehep.utils.record_getter import get_es_record
from .export import MissingRequiredFieldError, Export


class Latex(Export):

    """Class used to output LaTex format."""

    def __init__(self, record, latex_format):
        super(Latex, self).__init__(record)
        self.latex_format = latex_format

    def format(self):
        """Return LaTex export for single record."""
        formats = {
            'record': self._format_record,
        }
        return formats['record']()

    def _format_record(self):
        required_fields = ['author', 'title', 'publi_info', 'doi', 'arxiv']
        optional_fields = ['report_number', 'SLACcitation', 'citation_count']
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

    def _fetch_fields(self, req_fields, opt_fields=[]):
        fields = {
            'author': self._get_author,
            'title': self._get_title,
            'publi_info': self._get_publi_info,
            'doi': self._get_doi,
            'arxiv': self._get_arxiv,
            'report_number': self._get_report_number,
            'SLACcitation': self._get_slac_citation,
            'citation_count': self._get_citation_number
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
                out += u'  {},\n'.format(value[0])
            elif len(value) > 8:
                out += u'  {}'.format(value[0])
                if 'collaboration' in self.record:
                    try:
                        collaboration = self.\
                            record['collaboration'][0]['value']
                        if 'Collaboration' in collaboration:
                            out += u' {{\it et al.}} [' + collaboration +\
                                '],\n'
                        else:
                            out += u' {{\it et al.}} [' + collaboration +\
                                ' Collaboration],\n'
                    except IndexError:
                        pass
                else:
                    out += u' {\it et al.},\n'
            else:
                out += u'  {} and {},\n'.format(', '.join(value[:-1]),
                                                value[-1])
        elif field == 'title':
            out += u'  %``{},''\n'.format(value)
        elif field == 'publi_info':
            if isinstance(value, list):
                if len(value) > 1:
                    out += u'  {}\n    {}\n'.format('\n'.join(
                        value[:-1]), value[-1])
                else:
                    out += u'  {}\n'.format(value[0])
            else:
                out += u'  {}.\n'.format(value)
        elif field == 'doi':
            out += u'  {0}:{1}.\n'.format(field, value)
        elif field == 'arxiv':
            if self._get_publi_info():
                out += u'  [{}].\n'.format(value)
            else:
                out += u'  {}.\n'.format(value)
        elif field == 'report_number':
            out += u'  {}.\n'.format(value)
        elif field == 'SLACcitation':
            out += u'  {}\n'.format(value)
        elif field == 'citation_count':
            out += u'  %{}'.format(value)
        return out

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
                if 'full_name' in author and author['full_name']:
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
            for corp_author in self.record['corporate_author']:
                if corp_author:
                    first_last_match = re_last_first.search(corp_author)
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
        if 'titles' in self.record:
            if isinstance(self.record['titles'], list):
                for title in self.record['titles']:
                    if 'title' in title:
                        record_title = title['title']
                        break
            else:
                record_title = self.record['titles']['title'].strip()
            return re.sub(r'(?<!\\)([#&%])', r'\\\1', record_title)
        else:
            return record_title

    def _get_publi_info(self):
        result = []
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
                        if journal_letter and journal_title[-1] != ' ':
                            journal_letter = ' ' + journal_letter
                        journal_volume = journal_letter + ' {\\bf ' + \
                            field['journal_volume'][char_i:] + '}'
                    if 'year' in field:
                        if isinstance(field['year'], list):
                            year = ' (' + str(field['year'][-1]) + ')'
                        else:
                            year = ' (' + str(field['year']) + ')'
                    if 'journal_issue' in field:
                        if field['journal_issue']:
                            if self.latex_format == 'latex_eu':
                                journal_issue = ' ' + \
                                                field['journal_issue'] + ', '
                            else:
                                journal_issue = ', no. ' + \
                                                field['journal_issue']
                    if 'page_start' in field or 'artid' in field:
                        if self.latex_format == 'latex_eu':
                            pages = ' ' + (field.get('page_start') or field['artid'])
                        else:
                            pages = ', ' + (field.get('page_start') or field['artid'])
                    if self.latex_format == 'latex_eu':
                        out += journal_title + journal_volume + year + \
                            journal_issue + pages
                        result.append(out)
                    else:
                        out += journal_title + journal_volume + journal_issue \
                            + pages + year
                        result.append(out)
                if not result:
                    for field in self.record['publication_info']:
                        if 'pubinfo_freetext' in field and len(field) == 1:
                            return field['pubinfo_freetext']
            for k, v in enumerate(result):
                if k > 0:
                    v = '[' + v + ']'
                    result[k] = v
            return result

    def _get_report_number(self):
        """Return report number separated by commas"""
        if not (self._get_publi_info() or self._get_arxiv()):
            return super(Latex, self)._get_report_number()

    def _get_pubnote(self):
        """Return publication note"""
        journal, volume, pages = ['', '', '']
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            for field in pub_info:
                if 'journal_title' in field:
                    journal = field['journal_title']
                if 'journal_volume' in field:
                    volume = field['journal_volume']
                if 'page_start' in field or 'artid' in field:
                    pages = field.get('page_start') or field['artid']
                try:
                    if journal and (volume != '' or pages != ''):
                        recid = self.record['control_number']
                        record = get_es_record('jou', recid)
                        coden = ','.join(
                            [record['coden'][0], volume, pages])
                        return coden
                except Exception:
                    return ''
        else:
            return ''
