#
# This file is part of INSPIRE.
# Copyright (C) 2015 CERN.
##
# INSPIRE is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
##
# INSPIRE is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
##
# You should have received a copy of the GNU General Public License
# along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#

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


class Bibtex(object):

    """docstring for Bibtex"""

    def __init__(self, record):
        self.record = record
        self.entry_type, self.original_entry = self._get_entry_type()
        self.arxiv_field = self._get_arxiv_field()

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
        required_fields = ['key', 'author', 'editor', 'title',
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
                           for collections in self.record['collections']]
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
            if isinstance(pub_info, list):
                for field in pub_info:
                    if 'journal_title' in field and 'journal_volume' in field \
                            and 'page_artid' in field and 'year' in field:
                        entry_type = 'article'
                        break
            else:
                if 'journal_title' in pub_info \
                    and 'journal_volume' in pub_info \
                        and 'page_artid' in pub_info and 'year' in pub_info:
                    entry_type = 'article'
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

    def _get_citation_key(self):
        """Returns citation key for Bibtex"""
        result = []
        citation_key = ''
        if 'system_control_number' in self.record:
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
        if isinstance(citation_key, list):
            return citation_key[0].replace(' ', '')
        else:
            return citation_key.replace(' ', '')

    def _fetch_fields(self, req_fields, opt_fields=[]):
        fields = {
            'key': self._get_key,
            'author': self._get_author,
            'editor': self._get_editor,
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

    def _get_arxiv_field(self):
        """Return arXiv field if exists"""
        if 'report_number' in self.record:
            for field in self.record['report_number']:
                if ('source' in field and field['source'] == 'arXiv') \
                    or 'arxiv_category' in field or \
                    ('primary' in field and
                        field['primary'].upper().startswith('ARXIV:')):
                    return field

    def _get_key(self):
        """Returns record key"""
        key = ''
        if not self._get_citation_key():
            key = self.record['recid']
        return key

    def _get_author(self):
        """Return list of name(s) of the author(s)."""
        result = []
        spacinginitials = re.compile(r'([A-Z][a-z]{0,1}[}]?\.)(\b|[-\{])')
        if 'authors' in self.record:
            for author in self.record['authors']:
                if author['full_name']:
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
            if isinstance(self.record['corporate_author'], list):
                for corp_author in self.record['corporate_author']:
                    if 'corporate_author' in corp_author:
                        result.append(corp_author['corporate_author'])
            else:
                result.append(
                    self.record['corporate_author']['corporate_author'])
        return result

    def _get_editor(self):
        """Return the editors of the record"""
        result = []
        spacinginitials = re.compile(r'([A-Z][a-z]{0,1}[}]?\.)(\b|[-\{])')
        if 'authors' in self.record:
            if self.record['authors'][0]['relator_term'] and \
               self.record['authors'][0]['relator_term'] == 'ed.':
                result.append(spacinginitials.sub(
                            r'\1 \2', self.record['authors'][0]['full_name']))
            if result:
                return ''.join(editor for editor in result)

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
            return re.sub(r'(?<!\\)([#&%])', r'\\\1', record_title)
        else:
            return record_title

    def _get_organization(self):
        """Return record organization"""
        organization = ''
        if 'imprint' in self.record:
            for element in self.record['imprint']:
                if 'publisher' in element:
                    organization = element['publisher']
                    break
        return organization

    def _get_publisher(self):
        """Return record publisher"""
        publisher = ''
        if 'imprint' in self.record:
            for field in self.record['imprint']:
                if 'publisher' in field and field['publisher']:
                    publisher = field['publisher']
        return publisher

    def _get_address(self):
        """Return record address"""
        address = []
        if 'imprint' in self.record:
            for field in self.record['imprint']:
                if 'place' in field and field['place']:
                    address.append(field['place'])
            if address:
                if len(address) > 1:
                    return address[0]
                else:
                    if any(isinstance(i, list) for i in address):
                        from inspire.utils import bibtex_booktitle
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
                if 'affiliation' in author and author['affiliation']:
                    if len(author['affiliation']) > 1:
                        school = author['affiliation'][0]
                    else:
                        school = ''.join(affilation for affilation in
                                         author['affiliation'])
        return school

    def _get_booktitle(self):
        """Return record booktitle"""
        if self.entry_type == 'inproceedings' or \
           self.original_entry == 'inproceedings':
            from inspire.utils import bibtex_booktitle
            booktitle = bibtex_booktitle.generate_booktitle(self.record)
            if booktitle:
                bt = re.sub(r'(?<!\\)([#_&%$])', r'\\\1', booktitle)
                return '{' + bt + '}'

    def _get_year(self):
        """Return the publication year of the paper"""
        year = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            if isinstance(pub_info, list):
                for index, val in enumerate(pub_info):
                    if index == 0:
                        if 'year' in val:
                            year = val['year']
                if not year:
                    if 'imprint' in self.record:
                        for imprint in self.record['imprint']:
                            if 'date' in imprint:
                                year = imprint['date'].split('-')[0]
                    elif 'preprint_info' in self.record:
                        for preprint_info in self.record['preprint_info']:
                            if 'date' in preprint_info:
                                year = preprint_info['date'].split('-')[0]
            else:
                if 'year' in pub_info:
                    year = pub_info['year']
                elif 'preprint_info' in self.record:
                    year = self.record['preprint_info']['date'].split('-')[0]
        elif self.original_entry == 'thesis' and 'thesis' in self.record:
            for date in self.record['thesis']:
                if 'date' in date and date['date']:
                    year = date['date']
            if not year:
                if 'preprint_info' in self.record:
                    for preprint_info in self.record['preprint_info']:
                        if 'date' in preprint_info:
                            year = preprint_info['date'].split('-')[0]
                elif 'imprint' in self.record:
                    for imprint in self.record['imprint']:
                        if 'date' in imprint:
                            year = imprint['date'].split('-')[0]
        elif 'imprint' in self.record:
            for imprint in self.record['imprint']:
                if 'date' in imprint:
                    year = imprint['date'].split('-')[0]
        elif 'preprint_info' in self.record:
            for preprint_info in self.record['preprint_info']:
                if 'date' in preprint_info:
                    year = preprint_info['date'].split('-')[0]
        return year

    def _get_journal(self):
        """Return the publication journal of the paper"""
        journal_title = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            if isinstance(pub_info, list):
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
            else:
                if 'journal_title' in pub_info:
                    journal_title = re.sub(r'\.([A-Z])', r'. \1',
                                           pub_info['journal_title'])
        return journal_title

    def _get_volume(self):
        """Return the  journal volume of the paper"""
        volume = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            if isinstance(pub_info, list):
                try:
                    journal = pub_info[0]
                    if 'journal_volume' in journal:
                        if 'journal_title' in journal and \
                                        journal['journal_title'] == 'JHEP':
                            volume = re.sub(r'\d\d(\d\d)', r'\1',
                                            journal['journal_volume'])
                        else:
                            volume = journal['journal_volume']
                except IndexError:
                    pass
            else:
                if 'journal_volume' in pub_info:
                    if 'journal_title' in pub_info and \
                                    pub_info['journal_title'] == 'JHEP':
                        volume = re.sub(r'\d\d(\d\d)', r'\1',
                                        pub_info['journal_volume'])
                    else:
                        volume = pub_info['journal_volume']
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
            if isinstance(pub_info, list):
                try:
                    journal = pub_info[0]
                    if 'journal_issue' in journal:
                        number = journal['journal_issue']
                except IndexError:
                    pass
            else:
                if 'journal_issue' in pub_info:
                    number = pub_info['journal_issue']
        return number

    def _get_pages(self):
        """Return the journal pages of the paper"""
        pages = ''
        if 'publication_info' in self.record:
            pub_info = self.record['publication_info']
            if isinstance(pub_info, list):
                try:
                    journal = pub_info[0]
                    if 'page_artid' in journal:
                        if isinstance(journal['page_artid'], list):
                            pages = journal['page_artid'][-1]
                        else:
                            pages = journal['page_artid']
                except IndexError:
                    pass
            else:
                if 'page_artid' in pub_info:
                    pages = pub_info['page_artid']
        return pages

    def _get_doi(self):
        """Return page numbers"""
        if 'doi' in self.record:
            doi_list = []
            for doi in self.record['doi']:
                doi_list.append(doi['doi'])
            return ', '.join(doi for doi in list(set(doi_list)))
        else:
            return ''

    def _get_note(self):
        """Return record note"""
        if self.entry_type in ('article', 'inproceedings'):
            if 'publication_info' in self.record:
                pub_info = self.record['publication_info']
                if isinstance(pub_info, list):
                    result = ''
                    note_list = []
                    for index, val in enumerate(pub_info):
                        if index >= 1:
                            note = ''
                            if 'note' not in val and \
                                ('journal_title' in val
                                    or 'journal_volume' in val
                                    or 'journal_issue' in val
                                    or 'page_artid' in val
                                    or 'year' in val):
                                if 'journal_title' in val:
                                    if not ('journal_volume' in val or
                                            'journal_issue' in val
                                            or 'page_artid' in val
                                            or 'doi' in self.record):
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
                                if 'page_artid' in val:
                                    note += ',' + \
                                            val['page_artid'].split('-', 1)[0]
                                if 'year' in val:
                                    note += "(" + val['year'] + ")"
                                elif 'preprint_info' in self.record:
                                    for preprint_info in self.\
                                            record['preprint_info']:
                                        if 'date' in preprint_info:
                                            note += "(" + \
                                                    preprint_info['date']\
                                                    .split('-')[0] + ")"
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
                                if 'page_artid' in val:
                                    note += ',' + \
                                            val['page_artid'].split('-', 1)[0]
                                if 'year' in val:
                                    note += "(" + val['year'] + ")"
                                result = "[" + val['note'] + ": " + note + "]"
                                note_list.append(result)
                    if note_list:
                        return note_list[-1]
                return ''

    def _get_url(self):
        """Return url of the record"""
        result = ''
        if 'url' in self.record:
            for url in self.record['url']:
                if 'url' in url:
                    if isinstance(url['url'], list):
                        for element in url['url']:
                            if element.lower().endswith(
                                    ('.png', '.jpg', '.jpeg', '.gif', '.eps')):
                                continue
                            else:
                                result = url['url']
                                break
                    else:
                        if url['url'].lower().endswith(
                                ('.png', '.jpg', '.jpeg', '.gif', '.eps')):
                                continue
                        else:
                            result = url['url']
                            break
        return result

    def _get_eprint(self):
        """Return eprint"""
        result = []
        if self.arxiv_field:
            if self.arxiv_field['primary'].upper().startswith('ARXIV:'):
                result.append(self.arxiv_field['primary'][6:])
            else:
                result.append(self.arxiv_field['primary'])
        try:
            return result[0]
        except IndexError:
            return result

    def _get_archive_prefix(self):
        """Return archive prefix"""
        result = ''
        if 'report_number' in self.record:
            for field in self.record['report_number']:
                if 'source' in field:
                    result = field['source']
                elif 'arxiv_category' in field:
                    result = 'arXiv'
                elif 'primary' in field:
                    if field['primary'].upper().startswith('ARXIV:'):
                        result = 'arXiv'
        return result

    def _get_primary_class(self):
        """Return primary class"""
        if 'report_number' in self.record:
            for field in self.record['report_number']:
                if 'arxiv_category' in field:
                    return field['arxiv_category']
        else:
            return ''

    def _get_report_number(self):
        """Return report number separated by commas"""
        report_number = []
        if 'report_number' in self.record:
            for field in self.record['report_number']:
                if len(field) == 1:
                    report_number.append(field['primary'])
            return ', '.join(str(p) for p in report_number)
        else:
            return report_number

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
        isbn = []
        result = []
        if 'isbn' in self.record:
            for d in self.record['isbn']:
                isbn.append(d['isbn'])
            if len(isbn) > 1:
                for element in isbn:
                    if isinstance(element, list):
                        result.append(element[0])
                    else:
                        result.append(element)
                return ', '.join(element for element in result)
            else:
                if any(isinstance(i, list) for i in isbn):
                    from inspire.utils import bibtex_booktitle
                    nested_list = list(bibtex_booktitle.traverse(isbn))
                    return nested_list[0]
                else:
                    return ''.join(result for result in isbn)
        else:
            return isbn

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
                    cite_element = self\
                                   .record['report_number'][0]['primary']\
                                   .upper()
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
                                pages = pages.split('-')[0]
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
                            pages = pages.split('-')[0]
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
