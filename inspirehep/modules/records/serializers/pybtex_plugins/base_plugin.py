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

from pybtex.database.output import BaseWriter
import re
from inspirehep.utils.jinja2 import render_template_to_string_for_blueprint
from ...views import blueprint
from ..fields_export import MAX_AUTHORS_BEFORE_ET_AL


class PybtexBaseWriter(BaseWriter):
    """Shared writer class based on pybtex's BaseWriter for use in Inspire serializers."""

    # Way to separate records in the bibliography (style):
    RECORDS_SEPARATOR = '\n\n'

    # Which fields from the schema need to be passed to jinja2:
    TEMPLATE_FIELDS = ['doi', 'texkey', 'author', 'url', 'primaryClass', 'title', 'number', 'pages',
                       'volume', 'corporate_author', 'eprint', 'editor', 'year', 'publication_info_list',
                       'SLACcitation', 'eprint_new_style', 'journal', 'today', 'collaboration']

    def get_template_src(self):
        """
        :return: Source of the template file relative to records blueprint.
        """
        raise NotImplementedError()

    def process_entry(self, texkey, entry):
        """
        Preprocess values for display in the template.
        """
        fields = dict(entry.fields)

        template = {
            'author': self.format_persons(entry.persons['author']) if 'author' in entry.persons else None,
            'editor': self.format_persons(entry.persons['editor']) if 'editor' in entry.persons else None,
            'corporate_author': fields.get('author'),
            'publication_info_list': self.format_publication_list(fields.get('publication_info_list') or []),
        }

        return template

    def render_entry(self, texkey, entry):
        """
        Use the preprocessed template values to fill out a jinja2 template
        """
        template = self.process_entry(texkey, entry)

        for field in self.TEMPLATE_FIELDS:
            if field not in template:
                template[field] = dict(entry.fields).get(field)

        return render_template_to_string_for_blueprint(blueprint, self.get_template_src(), **template)

    def format_publication_list(self, pub_list):
        """
        Formats publication list: retrieves all the journal entries.
        """
        just_journals = []
        for i, pub in enumerate(pub_list):
            if 'journal' in pub:
                just_journals.append(pub)
        return just_journals

    def generate_initials(self, first_name):
        """
        Sometimes instead of a first_name we will find a cluster of initials like 'A.B.'
        This gets all the initials from either a cluster of them or a first_name.
        """
        if re.match('(\w{1}\.)+', first_name):
            return re.findall('(\w{1})\.', first_name)
        else:
            return [first_name[0]]

    def format_name(self, person):
        """
        Person is transformed into a string like "E. W. Dijkstra or J. von Neumann"
        """
        all_initials = sum([self.generate_initials(first_name) for first_name in person.bibtex_first_names], [])
        all_last_names = person.prelast_names + person.last_names
        formatted_person = '. '.join(all_initials) + '. ' + ' '.join(all_last_names)
        return formatted_person

    def format_persons(self, persons, and_others_string="et al."):
        """
        Generates a string out of a list of people.
        :param persons: list of objects type Person.
        """
        if len(persons) > MAX_AUTHORS_BEFORE_ET_AL:
            return self.format_name(persons[0]) + " " + and_others_string
        else:
            return ', '.join(self.format_name(person) for person in persons)

    def write_preamble(self, bib_data):
        """
        Defines the preamble, i.e. what to preceed the entries with.
        :param bib_data: BibliographyData.
        :return: String with the preamble.
        """
        return ""

    def write_postamble(self, bib_data):
        """
        Defines the postable, i.e. what to follow the entries with.
        :param bib_data: BibliographyData.
        :return: String with the postamble.
        """
        return ""

    def to_string(self, bib_data):
        """
        Dump the bibiography to string.
        [Note: overriden from pybtex.database.output.BaseWriter]
        :param bib_data: BibliographyData.
        :return: String with bibtex formatted bibliography.
        """
        bib_string = self.write_preamble(bib_data)
        bib_string += self.RECORDS_SEPARATOR.join(
            self.render_entry(texkey, entry) for texkey, entry in bib_data.entries.items()
        )
        bib_string += self.write_postamble(bib_data)
        return bib_string

    def write_stream(self, bib_data, stream):
        """
        See `self.to_string` but for outputting to a stream.
        [Note: overriden from pybtex.database.output.BaseWriter]
        """
        return print(self.to_string(bib_data), file=stream)

    def to_bytes(self, bib_data):
        """
        See `self.to_string` but for outputting to bytes.
        [Note: overriden from pybtex.database.output.BaseWriter]
        """
        return self.to_string(bib_data).encode('utf-8')
