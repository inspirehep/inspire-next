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

from .export import MissingRequiredFieldError, Export
from inspirehep import config


class Cv_latex_html_text(Export):

    """Class used to output CV format(html) and CV format(text)."""

    def __init__(self, record, format_type, separator):
        super(Cv_latex_html_text, self).__init__(record)
        self.record = record
        self.format_type = format_type
        self.separator = separator

    def format(self):
        """Return CV format export for single record."""
        formats = {
            'record': self._format_record,
        }
        return formats['record']()

    def _format_record(self):
        required_fields = ['title', 'author', 'arxiv']
        optional_fields = ['doi', 'publi_info']
        try:
            return self._format_entry(required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_entry(self, req, opt):
        """
        :raises: MissingRequiredFieldError
        """
        out = ''
        out += self._fetch_fields(req, opt) + '%s' % self.separator
        return out

    def _fetch_fields(self, req_fields, opt_fields=[]):
        fields = {
            'title': self._get_title,
            'author': self._get_author,
            'arxiv': self._get_arxiv,
            'doi': self._get_doi,
            'publi_info': self._get_publi_info,
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
        if field == 'title':
            if self.format_type == 'cv_latex_html':
                out += unicode('<a href="' + config.SERVER_NAME + '/record/' +
                               str(self.record['control_number']) + '">' +
                               value + '.</a>' + self.separator)
            else:
                out += u'{0}{1}'.format(value, self.separator)
        elif field == 'author':
            if len(value) == 1:
                out += u'By {0}.{1}'.format(value[0], self.separator)
            elif len(value) > 8:
                if 'collaboration' in self.record:
                    try:
                        collaboration = self.record[
                            'collaboration'][0]['value']
                        if 'Collaboration' in collaboration:
                            out += unicode('By ' + collaboration +
                                           '(' + value[0] + ' et al.).' +
                                           self.separator)
                        else:
                            out += unicode('By ' + collaboration +
                                           ' Collaboration (' +
                                           value[0] + ' et al.).' +
                                           self.separator)
                    except IndexError:
                        pass
                else:
                    out += u'By  {0} et al..{1}'.format(value[0],
                                                        self.separator)
            else:
                out += u'By {0}.{1}'.format(', '.join(value), self.separator)
        elif field == 'arxiv':
            if self.format_type == 'cv_latex_html':
                out += u'[{0}].{1}'.format(value, self.separator)
            else:
                out += u'{0}.{1}'.format(value, self.separator)
        elif field == 'doi':
            dois_splitted = value.split(',')
            for k, v in enumerate(dois_splitted):
                v = '<a href="http://dx.doi.org/' + v + '">' + v + '</a>'
                dois_splitted[k] = v
            out += u'{0}.{1}'.format(', '.join(out for out in dois_splitted),
                                     self.separator)
        elif field == 'publi_info':
            out += u'{0}.{1}'.format(', '.join(out for out in value),
                                     self.separator)
        return out

    def _get_author(self):
        """Return list of name(s) of the author(s)."""
        re_last_first = re.compile(
            r'^(?P<last>[^,]+)\s*,\s*(?P<first_names>[^\,]*)(?P<extension>\,?.*)$'
        )
        result = []
        if 'authors' in self.record:
            for author in self.record['authors']:
                if 'full_name' in author and author['full_name']:
                    if isinstance(author['full_name'], list):
                        author_full_name = ''.join(full_name for full_name
                                                   in author['full_name'])
                        first_last_match = re_last_first.search(
                            author_full_name)
                        if first_last_match:
                            result.append(
                                first_last_match.group('first_names') +
                                ' ' + first_last_match.
                                group('last') +
                                first_last_match.
                                group('extension')
                            )
                    else:
                        first_last_match = re_last_first.search(
                            author['full_name'])
                        if first_last_match:
                            result.append(
                                first_last_match.group('first_names') +
                                ' ' + first_last_match.
                                group('last') +
                                first_last_match.group('extension')
                            )
        elif 'corporate_author' in self.record:
            for corp_author in self.record['corporate_author']:
                if corp_author:
                    result.append(corp_author)
        return result

    def _get_title(self):
        """Return record title(s)"""
        record_title = ''
        if 'titles' in self.record:
            if isinstance(self.record['titles'], list):
                for title in self.record['titles']:
                    if 'title' in title:
                        record_title = title['title']
                        break
            else:
                record_title = self.record['titles']['title'].strip()

            if isinstance(self.record['titles'], list):
                for subtitle in self.record['titles']:
                    if 'subtitle' in subtitle and subtitle['subtitle']:
                        record_title += ' : ' + subtitle['subtitle']
                        break
            else:
                if 'subtitle' in self.record['titles']:
                    record_title += ' : ' + self.record['titles']['subtitle']
            if record_title.upper() == record_title or \
               record_title.find('THE') >= 0:
                record_title = ' '.join([word.capitalize() for word
                                         in record_title.split(' ')])
        return record_title

    def _get_publi_info(self):
        result = []
        if 'publication_info' in self.record:
            journal_title, journal_volume, year, journal_issue, pages = \
                ('', '', '', '', '')
            for field in self.record['publication_info']:
                out = ''
                if 'journal_title' in field:
                    journal_title = field['journal_title']
                    if 'journal_volume' in field:
                        journal_volume = ' ' + field['journal_volume']
                    if 'year' in field:
                        year = ' (' + str(field['year']) + ')'
                    if 'journal_issue' in field:
                        if field['journal_issue']:
                            journal_issue = ' ' + \
                                            field['journal_issue'] + ','
                    if 'page_start' in field and 'page_end' in field:
                        pages = ' {page_start}-{page_end}'.format(**field)
                    elif 'page_start' in field:
                        pages = ' {page_start}'.format(**field)
                    elif 'artid' in field:
                        pages = ' {artid}'.format(**field)
                    out += journal_title + journal_volume + year + \
                        journal_issue + pages
                    result.append(out)
            if not result:
                for field in self.record['publication_info']:
                    if 'pubinfo_freetext' in field and len(field) == 1:
                        return field['pubinfo_freetext']
            return result
