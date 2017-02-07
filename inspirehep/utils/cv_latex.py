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

import re
import time

from .export import MissingRequiredFieldError, Export
from inspirehep import config


class Cv_latex(Export):

    """Class used to output CV LaTex format."""

    def __init__(self, record):
        super(Cv_latex, self).__init__(record)

    def format(self):
        """Return CV LaTex export for single record."""
        formats = {
            'record': self._format_record,
        }
        return formats['record']()

    def _format_record(self):
        required_fields = ['title', 'author', 'arxiv']
        optional_fields = ['doi', 'publi_info', 'url', 'citation_count']
        try:
            return self._format_entry(required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_entry(self, req, opt):
        """
        :raises: MissingRequiredFieldError
        """
        out = '%\cite{' + self._get_citation_key() + '}\n'
        out += r'\item%{' + self._get_citation_key() + '}\n'
        out += self._fetch_fields(req, opt) + '\n'
        return out

    def _fetch_fields(self, req_fields, opt_fields=[]):
        fields = {
            'author': self._get_author,
            'title': self._get_title,
            'arxiv': self._get_arxiv,
            'doi': self._get_doi,
            'publi_info': self._get_publi_info,
            'url': self._get_url,
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
                out += u'  \\\\{{}}{}.\n'.format(value[0])
            elif len(value) > 8:
                out += u'  \\\\{{}}{}'.format(value[0])
                if 'collaboration' in self.record:
                    try:
                        if 'collaboration' in self.record:
                            collaboration = self.record['collaboration'][0]['value']
                            if 'Collaboration' in collaboration:
                                out += u' {\it et al.} [' + \
                                    collaboration + '].\n'
                            else:
                                out += u' {\it et al.} [' + \
                                    collaboration + ' Collaboration].\n'
                    except IndexError:
                        pass
                else:
                    out += u' {\it et al.}.\n'
            else:
                out += u'  \\\\{{}}{} and {}.\n'.format(
                    ', '.join(value[:-1]), value[-1]
                )
        elif field == 'title':
            out += u'{}\n'.format(value)
        elif field == 'publi_info':
            if isinstance(value, list):
                if len(value) > 1:
                    out += u'  \\\\{{}}{},  {}'.format(''.join(
                        value[:-1]), value[-1])
                else:
                    out += u'  \\\\{{}}{}.'.format(value[0])
            else:
                out += u'  \\\\{{}}{}.'.format(value)
            if self._get_date():
                out += ' %(' + str(self._get_date()) + ')\n'
        elif field == 'arxiv':
            out += u'  \\\\{{}}{}.\n'.format(value)
        elif field == 'doi':
            out += u'    \\\\{{}}{}.\n'.format(value)
        elif field == 'url':
            out += u' %\href{{{}}}{{HEP entry}}.\n'.format(value)
        elif field == 'citation_count':
            out += u' %{}'.format(value)
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
            return r"{\bf ``" + re.sub(
                r'(?<!\\)([#&%])', r'\\\1', record_title
            ) + "''}"
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
                        journal_title = field[
                            'journal_title'][-1].replace(".", '.\\ ')
                    else:
                        journal_title = field[
                            'journal_title'].replace(".", '.\\ ')
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
                            journal_issue = ', no. ' + field['journal_issue']
                    if 'page_start' in field or 'artid' in field:
                        pages = ', ' + (field.get('page_start') or field['artid'])

                    out += journal_title + journal_volume + journal_issue + \
                        pages + year
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

    def _get_url(self):
        return config.SERVER_NAME + '/record/' + \
            str(self.record['control_number'])

    def _get_date(self):
        """Returns date looking for every case"""
        datestruct = ''
        if 'preprint_date' in self.record:
            datestruct = self.parse_date(str(self.record['preprint_date']))
            if datestruct:
                return self._format_date(datestruct)  # FIX ME ADD 0 IN THE DAY

        if self.arxiv_field:
            date = re.search('(\d+)',
                             self.arxiv_field['value']).groups()[0]
            if len(date) >= 4:
                year = date[0:2]
                if year > '90':
                    year = '19' + year
                else:
                    year = '20' + year
                date = year + date[2:4]  # FIX ME DONT ADD 00 AS A DAY
                date = self.parse_date(str(date))
                if date:
                    return self._format_date(date)

        if 'publication_info' in self.record:
            for field in self.record['publication_info']:
                if 'year' in field:
                    date = field['year']
                    if date:
                        datestruct = self.parse_date(str(date))
                    break
            if datestruct:
                return self._format_date(datestruct)

        if 'legacy_creation_date' in self.record:
            datestruct = self.parse_date(str(self.record['legacy_creation_date']))
            if datestruct:
                return self._format_date(datestruct)

        if 'imprints' in self.record:
            for field in self.record['imprints']:
                if 'date' in field:
                    date = field['date']
                    if date:
                        datestruct = self.parse_date(str(date))
                    break
            if datestruct:
                return self._format_date(datestruct)

        if 'thesis' in self.record and 'date' in self.record['thesis']:
            date = self.record['thesis']['date']
            if date:
                datestruct = self.parse_date(str(date))
            if datestruct:
                return self._format_date(datestruct)

        return None

    def _format_date(self, datestruct):
        """Returns date formatted"""
        dummy_time = (0, 0, 44, 2, 320, 0)
        if len(datestruct) == 3:
            datestruct = tuple(datestruct[0:3]) + dummy_time
            return time.strftime("%b %-d, %Y", datestruct)
        elif len(datestruct) == 2:
            datestruct = tuple(datestruct[0:2]) + (1,) + dummy_time
            return time.strftime("%b %Y", datestruct)
        elif len(datestruct) == 1:
            return datestruct[0]
        return None

    def parse_date(self, datetext):
        """
        Reads in a date-string of either native spires (YYYYMMDD)
        or invenio style
        (YYYY-MM-DD). Then as much of the date as we have is returned
        in a tuple.
        @param datetext: date from record
        @type datetext: str
        @return: tuple of 1 or more integers, up to max (year, month, day).
            Otherwise None.
        """
        if datetext in [None, ""] or type(datetext) != str:
            return None
        datetext = datetext.strip()
        datetext = datetext.split(' ')[0]
        datestruct = []
        if "-" in datetext:
            # Looks like YYYY-MM-DD
            for date in datetext.split('-'):
                if date:
                    try:
                        datestruct.append(int(date))
                        continue
                    except ValueError:
                        pass
                break
        else:
            # Looks like YYYYMMDD
            try:
                # year - YYYY
                year = datetext[:4]
                if year == "":
                    return tuple(datestruct)
                datestruct.append(int(year))
                # month - MM
                month = datetext[4:6]
                if month == "":
                    return tuple(datestruct)
                datestruct.append(int(month))
                day = datetext[6:8]
                # day - DD
                if day == "":
                    return tuple(datestruct)
                datestruct.append(int(day))
            except ValueError:
                pass
        return tuple(datestruct)
