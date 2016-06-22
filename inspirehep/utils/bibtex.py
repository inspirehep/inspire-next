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

from dojson.utils import force_list

from inspirehep.utils import bibtex_booktitle
from inspirehep.utils.record_getter import get_es_record
from inspirehep.utils.record import is_submitted_but_not_published

from .export import MissingRequiredFieldError, Export


class Bibtex(Export):

    """Docstring for Bibtex"""

    def __init__(self, record):
        super(Bibtex, self).__init__(record)
        self.entry_type, self.original_entry = self._get_entry_type()

    def format(self):
        """Return BibTeX export for single record."""
        formats = {
            'article': self._format_article,
            'inproceedings': self._format_inproceeding,
            'proceedings': self._format_proceeding,
            'thesis': self._format_thesis,
            'book': self._format_book,
            'inbook': self._format_inbook,
        }
        if self.entry_type in formats:
            return formats[self.entry_type]()

    def _format_article(self):
        """Format article entry type"""
        name = "article"
        required_fields = ['key', 'author', 'editor', 'title', 'collaboration',
                           'booktitle', 'journal', 'volume']
        optional_fields = ['year', 'number', 'pages', 'doi', 'note',
                           'eprint', 'archivePrefix', 'primaryClass',
                           'reportNumber', 'SLACcitation']
        try:
            return self._format_entry(name, required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_inproceeding(self):
        """Format inproceedings entry type"""
        name = "inproceedings"
        required_fields = ['key', 'author', 'editor', 'title', 'organization',
                           'publisher', 'address', 'booktitle',
                           'url', 'journal', 'volume']
        optional_fields = ['year', 'number', 'pages', 'doi', 'note',
                           'eprint', 'archivePrefix', 'primaryClass',
                           'reportNumber', 'SLACcitation']
        try:
            return self._format_entry(name, required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_proceeding(self):
        """Format proceedings entry type"""
        name = "proceedings"
        required_fields = ['key', 'author', 'editor', 'title', 'organization',
                           'publisher', 'address', 'booktitle',
                           'url', 'journal', 'volume']
        optional_fields = ['year', 'number', 'pages', 'doi', 'note',
                           'eprint', 'archivePrefix', 'primaryClass',
                           'reportNumber', 'series', 'ISBN', 'SLACcitation']
        try:
            return self._format_entry(name, required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_thesis(self):
        """Format thesis entry type"""
        thesis = ''
        if 'thesis' in self.record:
            for type_of_thesis in self.record['thesis']:
                if 'degree_type' in type_of_thesis:
                    thesis = type_of_thesis['degree_type']
            if thesis == 'Master':
                name = 'mastersthesis'
            else:
                name = 'phdthesis'
        else:
            name = 'phdthesis'
        required_fields = ['key', 'author', 'title', 'address',
                           'school', 'journal', 'volume']
        optional_fields = ['year', 'url', 'number', 'pages', 'doi', 'note',
                           'eprint', 'archivePrefix', 'primaryClass',
                           'reportNumber', 'SLACcitation']
        try:
            return self._format_entry(name, required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_book(self):
        """Format book entry type"""
        name = "book"
        required_fields = ['key', 'author', 'editor', 'title', 'publisher',
                           'address', 'booktitle', 'url', 'volume']
        optional_fields = ['year', 'number', 'doi', 'note',
                           'eprint', 'archivePrefix', 'primaryClass',
                           'reportNumber', 'series', 'ISBN', 'SLACcitation']
        try:
            return self._format_entry(name, required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _format_inbook(self):
        """Format inbook entry type"""
        name = "inbook"
        required_fields = ['key', 'author', 'editor', 'title', 'publisher',
                           'address', 'booktitle', 'url', 'volume']
        optional_fields = ['year', 'number', 'pages', 'doi', 'note',
                           'eprint', 'archivePrefix', 'primaryClass',
                           'reportNumber', 'series', 'SLACcitation']
        try:
            return self._format_entry(name, required_fields, optional_fields)
        except MissingRequiredFieldError as e:
            raise e

    def _get_entry_type(self):
        """Returns the type of record"""
        entry_type = 'article'
        if 'collections' in self.record:
            collections = [collections["primary"].lower()
                           for collections in self.record['collections']
                           if 'primary' in collections]
            if 'conferencepaper' in collections:
                entry_type = 'inproceedings'
            elif 'thesis' in collections:
                entry_type = 'thesis'
            elif 'proceedings' in collections:
                entry_type = 'proceedings'
            elif 'book' in collections:
                entry_type = 'book'
            elif 'bookchapter' in collections:
                entry_type = 'inbook'
            elif 'arxiv' in collections or 'published'in collections:
                entry_type = 'article'
        original_entry = entry_type
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            for field in pub_info:
                if 'journal_title' in field and 'journal_volume' in field \
                        and ('page_start' in field or 'artid' in field) \
                        and 'year' in field:
                    entry_type = 'article'
                    break
        return entry_type, original_entry

    def _format_entry(self, name, req, opt):
        """
        :raises: MissingRequiredFieldError
        """
        out = '@' + name + '{'
        out += self._get_citation_key() + ',\n'
        out += self._fetch_fields(req, opt) + '\n'
        out += '}'
        return out

    def _fetch_fields(self, req_fields, opt_fields=[]):
        fields = {
            'key': self._get_key,
            'author': self._get_author,
            'editor': self._get_editor,
            'collaboration': self._get_collaboration,
            'title': self._get_title,
            'organization': self._get_organization,
            'publisher': self._get_publisher,
            'address': self._get_address,
            'school': self._get_school,
            'booktitle': self._get_booktitle,
            'url': self._get_url,
            'journal': self._get_journal,
            'year': self._get_year,
            'volume': self._get_volume,
            'number': self._get_number,
            'pages': self._get_pages,
            'eprint': self._get_eprint,
            'archivePrefix': self._get_archive_prefix,
            'primaryClass': self._get_primary_class,
            'reportNumber': self._get_report_number,
            'doi': self._get_doi,
            'note': self._get_note,
            'series': self._get_series,
            'ISBN': self._get_isbn,
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
                out += u'      {0:<14} = \"{1}\",\n'.format(field, value[0])
            else:
                out += u'      {0:<14} = \"{1} and '.format(field, value[0])
            if len(value) > 1:
                if len(value) > 10:
                    out += u'others\",\n'
                else:
                    for line in value[1:-1]:
                        out += u'{1:<} and '.format("", line)
                    out += u'{1:<}\",\n'.format("", value[-1])
        elif field == 'title':
            out += u'      {0:<14} = \"{{{1}}}\",\n'.format(field, value)
        elif field == 'doi':
            out += u'      {0:<14} = \"{1}\",\n'.format(field, value)
        elif field == 'SLACcitation':
            out += u'      {0:<14} = \"{1}\"'.format(field, value)
        else:
            if self._is_number(value):
                out += u'      {0:<14} = \"{1}\",\n'.format(field, value)
            else:
                out += u'      {0:<14} = \"{1}\",\n'.format(field, value)
        return out

    def _is_number(self, s):
        try:
            int(s)
            return True
        except (ValueError, TypeError):
            return False

    def _get_key(self):
        """Returns record key"""
        key = ''
        if not self._get_citation_key():
            key = self.record['control_number']
        return key

    def _get_author(self):
        """Return list of name(s) of the author(s)."""
        result = []
        spacinginitials = re.compile(r'([A-Z][a-z]{0,1}[}]?\.)(\b|[-\{])')
        if 'authors' in self.record:
            for author in self.record['authors']:
                if 'full_name' in author and author['full_name']:
                    if isinstance(author['full_name'], list):
                        author_full_name = 'and '.join(full_name for full_name
                                                       in author['full_name'])
                        result.append(spacinginitials.sub(
                            r'\1 \2', author_full_name))
                    else:
                        author_full_name = spacinginitials.sub(
                            r'\1 \2', author['full_name'])
                        result.append(author_full_name)
        elif 'corporate_author' in self.record:
            for corp_author in self.record['corporate_author']:
                if corp_author:
                    result.append(corp_author)
        return result

    def _get_editor(self):
        """Return the editors of the record"""
        result = []
        spacinginitials = re.compile(r'([A-Z][a-z]{0,1}[}]?\.)(\b|[-\{])')
        if 'authors' in self.record:
            if self.record['authors'][0].get('role') == 'ed.':
                result.append(spacinginitials.sub(
                    r'\1 \2', self.record['authors'][0]['full_name']
                ))
            if result:
                return ''.join(editor for editor in result)

    def _get_title(self):
        """Return record titles"""
        record_title = ''
        if 'titles' in self.record:
            titles = force_list(self.record['titles'])
            for title in titles:
                if 'title' in title:
                    record_title = title['title']
                    break
            return re.sub(r'(?<!\\)([#&%])', r'\\\1', record_title)
        else:
            return record_title

    def _get_collaboration(self):
        """Return collaboration"""
        collaboration = ''
        if 'collaboration' in self.record:
            try:
                collaboration = self.record['collaboration'][0]['value']
            except (IndexError, KeyError):
                pass
        return collaboration

    def _get_organization(self):
        """Return record organization"""
        organization = ''
        if 'imprints' in self.record:
            for element in self.record['imprints']:
                if 'publisher' in element:
                    organization = element['publisher']
                    break
        return organization

    def _get_publisher(self):
        """Return record publisher"""
        publisher = ''
        if 'imprints' in self.record:
            for field in self.record['imprints']:
                if 'publisher' in field and field['publisher']:
                    publisher = field['publisher']
        return publisher

    def _get_address(self):
        """Return record address"""
        address = []
        if 'imprints' in self.record:
            for field in self.record['imprints']:
                if 'place' in field and field['place']:
                    address.append(field['place'])
            if address:
                if len(address) > 1:
                    return address[0]
                else:
                    if any(isinstance(i, list) for i in address):
                        nested_list = list(bibtex_booktitle.traverse(address))
                        return nested_list[0]
                    else:
                        return ''.join(result for result in address)
        else:
            return address

    def _get_school(self):
        """Return record school"""
        school = ''
        if 'authors' in self.record:
            for author in self.record['authors']:
                if author.get('affiliations'):
                    if len(author['affiliations']) > 1:
                        school = author['affiliations'][0]['value']
                    else:
                        school = ''.join(affilation.get('value') for affilation in
                                         author['affiliations'])
        return school

    def _get_booktitle(self):
        """Return record booktitle"""
        if self.entry_type == 'inproceedings' or \
           self.original_entry == 'inproceedings':
            booktitle = bibtex_booktitle.generate_booktitle(self.record)
            if booktitle:
                bt = re.sub(r'(?<!\\)([#_&%$])', r'\\\1', booktitle)
                return '{' + bt + '}'

    def _get_year(self):
        """Return the publication year of the paper"""
        year = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            for index, val in enumerate(pub_info):
                if index == 0:
                    if 'year' in val:
                        year = val['year']
            if not year:
                if 'imprints' in self.record:
                    for imprint in self.record['imprints']:
                        if 'date' in imprint:
                            year = imprint['date'].split('-')[0]
                elif 'preprint_date' in self.record:
                    year = self.record['preprint_date'][0].split('-')[0]
        elif self.original_entry == 'thesis' and 'thesis' in self.record:
            for date in self.record['thesis']:
                if 'date' in date and date['date']:
                    year = date['date']
            if not year:
                if 'preprint_date' in self.record:
                    year = self.record['preprint_date'].split('-')[0]
                elif 'imprints' in self.record:
                    for imprint in self.record['imprints']:
                        if 'date' in imprint:
                            year = imprint['date'].split('-')[0]
        elif 'imprints' in self.record:
            for imprint in self.record['imprints']:
                if 'date' in imprint:
                    year = imprint['date'].split('-')[0]
        elif 'preprint_date' in self.record:
            for date in self.record['preprint_date']:
                if date is not None:
                    year = date.split('-')[0]
                break
        return year

    def _get_journal(self):
        """Return the publication journal of the paper"""
        journal_title = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            try:
                journal = pub_info[0]
                if 'journal_title' in journal:
                    if isinstance(journal['journal_title'], list):
                        journal_title = journal['journal_title'][-1]
                    else:
                        journal_title = re.sub(r'\.([A-Z])', r'. \1',
                                               journal['journal_title'])
            except IndexError:
                pass
        return journal_title

    def _get_volume(self):
        """Return the  journal volume of the paper"""
        volume = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            try:
                journal = pub_info[0]
                if 'journal_volume' in journal:
                    if 'journal_title' in journal and \
                            journal['journal_title'] == 'JHEP':
                        volume = re.sub(
                            r'\d\d(\d\d)', r'\1',
                            journal['journal_volume']
                        )
                    else:
                        volume = journal['journal_volume']
            except IndexError:
                pass
            if not volume:
                if 'book_series' in self.record:
                    for field in self.record['book_series']:
                        if 'volume' in field:
                            volume = field['volume']
        elif 'book_series' in self.record:
            for field in self.record['book_series']:
                if 'volume' in field:
                    volume = field['volume']
        return volume

    def _get_number(self):
        """Return the  journal number of the paper"""
        number = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            try:
                journal = pub_info[0]
                if 'journal_issue' in journal:
                    number = journal['journal_issue']
            except IndexError:
                pass
        return number

    def _get_pages(self):
        """Return the journal pages of the paper"""
        pages = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            try:
                journal = pub_info[0]
                if 'page_start' in journal and 'page_end' in journal:
                    pages = '{page_start}-{page_end}'.format(**journal)
                elif 'page_start' in journal:
                    pages = '{page_start}'.format(**journal)
                elif 'artid' in journal:
                    pages = '{artid}'.format(**journal)
            except IndexError:
                pass
        return pages

    def _get_note(self):
        """Return record note"""
        if self.entry_type in ('article', 'inproceedings'):
            if 'publication_info' in self.record:
                pub_info = self.record['publication_info']
                result = ''
                note_list = []
                for index, val in enumerate(pub_info):
                    if index >= 1:
                        note = ''
                        if 'note' not in val and \
                            ('journal_title' in val or
                             'journal_volume' in val or
                             'journal_issue' in val or
                             'page_start' in val or
                             'artid' in val or
                             'year' in val):
                            if 'journal_title' in val:
                                if is_submitted_but_not_published(self.record):
                                    note += 'Submitted to: ' +\
                                            re.sub(r'\.([A-Z])', r'. \1',
                                                   val['journal_title'])
                                else:
                                    note += re.sub(r'\.([A-Z])', r'. \1',
                                                   val['journal_title'])
                                    if 'journal_volume' in val:
                                        if note.find("JHEP") > -1:
                                            note += re.sub(r'\d\d(\d\d)', r'\1',
                                                           val['journal_volume'])
                                        else:
                                            note += val['journal_volume']
                                    if 'journal_issue' in val:
                                        note += ',no.' + val['journal_issue']
                                    if 'page_start' in val or 'artid' in val:
                                        note += ',' + (val.get('page_start') or val['artid'])
                            if 'year' in val:
                                note += "(" + str(val['year']) + ")"
                            elif 'preprint_date' in self.record:
                                note += "(" + str(self.record['preprint_date'].split('-')[0]) + ")"
                            result = '[' + note + ']'
                            note_list.append(result)
                        elif 'note' in val and \
                            (val['note'] in ('Erratum', 'Addendum',
                                             'Corrigendum', 'Reprint')):
                            if 'journal_title' in val:
                                note += re.sub(r'\.([A-Z])', r'. \1',
                                               val['journal_title'])
                            if 'journal_volume' in val:
                                if note.find("JHEP") > -1:
                                    note += re.sub(r'\d\d(\d\d)', r'\1',
                                                   val['journal_volume'])
                                else:
                                    note += val['journal_volume']
                            if 'journal_issue' in val:
                                note += ',no.' + val['journal_issue']
                            if 'page_start' in val or 'artid' in val:
                                note += ',' + (val.get('page_start') or val['artid'])
                            if 'year' in val:
                                note += "(" + str(val['year']) + ")"
                            result = "[" + val['note'] + ": " + note + "]"
                            note_list.append(result)
                if note_list:
                    return note_list[-1]
                return ''

    def _get_url(self):
        """Return url of the record"""
        result = ''
        if 'urls' in self.record:
            for url in self.record['urls']:
                if 'value' in url:
                    if url['value'].lower().endswith(
                            ('.png', '.jpg', '.jpeg', '.gif', '.eps')):
                        continue
                    else:
                        result = url['value']
                        break
        return result

    def _get_eprint(self):
        """Return eprint"""
        result = []
        if self.arxiv_field:
            if self.arxiv_field['value'].upper().startswith('ARXIV:'):
                result.append(self.arxiv_field['value'][6:])
            else:
                result.append(self.arxiv_field['value'])
        try:
            return result[0]
        except IndexError:
            return result

    def _get_archive_prefix(self):
        """Return archive prefix"""
        result = ''
        if 'arxiv_eprints' in self.record and\
                len(self.record['arxiv_eprints']):
            result = "arXiv"
        return result

    def _get_primary_class(self):
        """Return primary class"""
        if 'arxiv_eprints' in self.record:
            for field in self.record['arxiv_eprints']:
                if 'categories' in field:
                    return field['categories'][0]
        else:
            return ''

    def _get_series(self):
        """Return series"""
        series = ''
        if 'book_series' in self.record:
            for element in self.record['book_series']:
                if 'value' in element:
                    series = element['value']
        return series

    def _get_isbn(self):
        """Return ISBN"""
        isbn_list = []
        result = []
        if 'isbns' in self.record:
            for isbn in self.record['isbns']:
                isbn_list.append(isbn['value'])
            if len(isbn_list) > 1:
                for element in isbn_list:
                    if isinstance(element, list):
                        result.append(element[0])
                    else:
                        result.append(element)
                return ', '.join(element for element in result)
            else:
                if any(isinstance(i, list) for i in isbn):
                    nested_list = list(bibtex_booktitle.traverse(isbn))
                    return nested_list[0]
                else:
                    return ''.join(result for result in isbn)
        else:
            return ''

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
                    pages = field.get('page_start', '') or field.get('artid', '')
                try:
                    if journal and (volume != '' or pages != ''):
                        recid = self.record['control_number', '']
                        record = get_es_record('journals', recid)
                        coden = ','.join(
                            [record['coden'][0], volume, pages])
                        return coden
                except:
                    return ''
        else:
            return ''
