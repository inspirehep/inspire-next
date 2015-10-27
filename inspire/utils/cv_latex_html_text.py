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

from invenio_base.globals import cfg

from .export import MissingRequiredFieldError, Export


class Cv_latex_html_text(Export):

    """Class used to output CV format(html) and CV format(text)."""

    def __init__(self, record, format_type):
        super(Cv_latex_html_text, self).__init__(record)
        self.record = record
        self.arxiv_field = self._get_arxiv_field()
        self.format_type = format_type

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
        out += self._fetch_fields(req, opt) + '<br/>'
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
                out += u'<a href="' + cfg['CFG_SITE_URL'] + '/record/' + \
                    str(self.record['control_number']) + '">' \
                    + '{1}.</a><br/>'.format(field, value)
            else:
                out += u'{1}<br/>'.format(field, value)
        elif field == 'author':
            if len(value) == 1:
                out += u'By {1}.<br/>'.format(field, value[0])
            elif len(value) > 8:
                if 'collaboration' in self.record:
                    try:
                        if 'collaboration' in self.record['collaboration'][0]:
                            collaboration = self.record['collaboration'][0]['collaboration']
                            if 'Collaboration' in collaboration:
                                out += u'By ' + collaboration + '({1} et al.).<br/>'.format(
                                    field, value[0]
                                )
                            else:
                                out += u'By ' + collaboration + ' Collaboration ({1} et al.).<br/>'.format(
                                    field, value[0]
                                )
                    except IndexError:
                        pass
                else:
                    out += u'By  {1} et al..<br/>'.format(field, value[0])
            else:
                out += u'By {}.<br/>'.format(', '.join(value))
        elif field == 'arxiv':
            if self.format_type == 'cv_latex_html':
                out += u'[{1}].<br/>'.format(field, value)
            else:
                out += u'{1}.<br/>'.format(field, value)
        elif field == 'doi':
            out += u'<a href="http://dx.doi.org/{1}">{1}</a>.<br/>'.format(
                field, value
            )
        elif field == 'publi_info':
            out += u'{1}.<br/>'.format(field, value)
        return out

    def _get_author(self):
        """Return list of name(s) of the author(s)."""
        re_last_first = re.compile(
            r'^(?P<last>[^,]+)\s*,\s*(?P<first_names>[^\,]*)(?P<extension>\,?.*)$'
        )
        result = []
        if 'authors' in self.record:
            for author in self.record['authors']:
                if author['full_name']:
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
        if 'title' in self.record:
            if isinstance(self.record['titles'], list):
                for title in self.record['titles']:
                    if 'title' in title:
                        record_title = title['title']
                        break
            else:
                record_title = self.record['titles']['title'].strip()

            if isinstance(self.record['titles'], list):
                for subtitle in self.record['titles']:
                    if 'subtitle' in subtitle:
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
        if 'publication_info' in self.record:
            journal_title, journal_volume, year, journal_issue, pages = \
                ('', '', '', '', '')
            for field in self.record['publication_info']:
                out = ''
                if 'journal_title' in field:
                    if isinstance(field['journal_title'], list):
                        if not ('journal_volume' in field or
                                'journal_issue' in field or
                                'page_artid' in field or
                                'doi' in self.record):
                            journal_title = 'Submitted to:' +\
                                field['journal_title'][-1]
                        else:
                            journal_title = field['journal_title'][-1]
                    else:
                        if not ('journal_volume' in field or
                                'journal_issue' in field or
                                'page_artid' in field or
                                'doi' in self.record):
                            journal_title = 'Submitted to:' +\
                                field['journal_title']
                        else:
                            journal_title = field['journal_title']
                    if 'journal_volume' in field:
                        journal_volume = ' ' + field['journal_volume']
                    if 'year' in field:
                        if isinstance(field['year'], list):
                            year = ' (' + field['year'][-1] + ')'
                        else:
                            year = ' (' + field['year'] + ')'
                    if 'journal_issue' in field:
                        if field['journal_issue']:
                                journal_issue = ' ' + \
                                                field['journal_issue'] + ','
                    if 'page_artid' in field:
                        if field['page_artid']:
                            if isinstance(field['page_artid'], list):
                                pages = ' ' + field['page_artid'][-1]
                            else:
                                pages = ' ' + field['page_artid']
                    break
                else:
                    if 'pubinfo_freetext' in field and len(field) == 1:
                        return field['pubinfo_freetext']
            out += journal_title + journal_volume + year + \
                journal_issue + pages
            if out:
                return out
