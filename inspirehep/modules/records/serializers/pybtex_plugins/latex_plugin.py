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

from ...views import blueprint
import datetime
from inspirehep.utils.jinja2 import render_template_to_string_for_blueprint
from inspirehep import config
from . import PybtexBaseWriter


class LatexWriter(PybtexBaseWriter):
    """Outputs Latex"""

    TEMPLATE_FIELDS = ['citation_count', 'doi', 'texkey', 'author', 'url', 'primaryClass', 'title', 'number', 'pages',
                       'volume', 'corporate_author', 'eprint', 'editor', 'year', 'publication_info_list',
                       'SLACcitation', 'eprint_new_style', 'journal', 'today', 'collaboration']

    def __init__(self, style):
        if style not in ('latex_us', 'latex_eu', 'latex_cv'):
            raise NotImplementedError('Only latex_us, latex_eu and latex_cv output formats are supported')
        else:
            self.style = style

    def get_template_src(self):
        """
        :return: Source of the template file relative to records blueprint.
        """
        return 'records/{}.tex'.format(self.style)

    def process_entry(self, texkey, entry):
        """
        Preprocess values for display in the template.
        """
        fields = dict(entry.fields)
        template = super(LatexWriter, self).process_entry(texkey, entry)
        new_template = {
            'texkey': texkey,
            'doi': fields.get('doi', '').replace('_', r'\_'),
            'today': datetime.datetime.now().strftime("%-d %b %Y"),
            'url': 'http://' + config.SERVER_NAME + '/record/' + fields['key'],
            'citation_count': fields.get('citation_count') or 0,
            'primaryClasses': fields.get('primaryClasses')
        }
        template.update(new_template)
        return template

    def render_entry(self, texkey, entry):
        """
        Use the preprocessed template values to fill out a jinja2 template
        """
        template = self.process_entry(texkey, entry)

        for field in LatexWriter.TEMPLATE_FIELDS:
            if field not in template:
                template[field] = dict(entry.fields).get(field)

        return render_template_to_string_for_blueprint(blueprint, self.get_template_src(), **template)

    def format_publication_list(self, pub_list):
        """
        Formats publication list: every element is transformed to latex friendly,
        and non-journal entries are discarded (if any).
        """
        just_journals = []
        for i, pub in enumerate(pub_list):
            if 'journal' in pub:
                pub['journal'] = pub['journal'].replace('.', r'.\ ')
                just_journals.append(pub)
        return just_journals

    def format_name(self, person):
        """
        Person is transformed into a LaTeX-friendly string like "E.~W.~Dijkstra or J.~von Neumann"
        """
        return super(LatexWriter, self).format_name(person).replace('. ', '.~')

    def format_persons(self, persons):
        """
        Generates a string out of a list of people.
        :param persons: list of objects type Person.
        """
        return super(LatexWriter, self).format_persons(persons, "{\it et al.}")

    def write_preamble(self, bib_data):
        """
        Defines the preamble, i.e. what to preceed the entries with.
        :param bib_data: BibliographyData.
        :return: String with the preamble.
        """
        if len(bib_data.entries) > 1:
            return r"\begin{thebibliography}{" + str(len(bib_data.entries)) + "}\n\n"
        else:
            return ""

    def write_postamble(self, bib_data):
        """
        Defines the postable, i.e. what to follow the entries with.
        :param bib_data: BibliographyData.
        :return: String with the postamble.
        """
        if len(bib_data.entries) > 1:
            return "\n\n\\end{thebibliography}"
        else:
            return ""

    def to_string(self, bib_data):
        """
        Dump the bibiography to string.
        :param bib_data: BibliographyData.
        :return: String with bibtex formatted bibliography.
        """
        bib_string = self.write_preamble(bib_data)
        bib_string += '\n\n'.join(self.render_entry(texkey, entry) for texkey, entry in bib_data.entries.items())
        bib_string += self.write_postamble(bib_data)
        return bib_string
