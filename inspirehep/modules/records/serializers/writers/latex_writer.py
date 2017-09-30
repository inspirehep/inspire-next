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

import datetime
from flask import current_app
from . import PybtexBaseWriter


class LatexWriter(PybtexBaseWriter):
    """Outputs Latex"""

    ACCEPTED_FORMATS = ['latex_us', 'latex_eu']

    TEMPLATE_FIELDS = PybtexBaseWriter.TEMPLATE_FIELDS + ['citation_count']

    def __init__(self, style):
        if style not in LatexWriter.ACCEPTED_FORMATS:
            raise NotImplementedError('Only latex_us, latex_eu output formats are supported')
        else:
            self.style = style

    def get_template_src(self):
        """
        Returns:
            Source of the template file relative to records blueprint.
        """
        return 'records/{}.tex'.format(self.style)

    def process_entry(self, texkey, entry):
        """
        See Also:
            BaseWriter.process_entry
        """
        fields = dict(entry.fields)
        template = super(LatexWriter, self).process_entry(texkey, entry)
        new_template = {
            'texkey': texkey,
            'doi': fields.get('doi', '').replace('_', r'\_'),
            'today': datetime.datetime.now().strftime("%-d %b %Y"),
            'url': 'http://' + current_app.config['SERVER_NAME'] + '/record/' + fields['key'],
            'citation_count': fields.get('citation_count') or 0,
            'primaryClasses': fields.get('primaryClasses')
        }
        template.update(new_template)
        return template

    def format_publication_list(self, pub_list):
        """
        See Also:
            BaseWriter.format_publication_list
        """
        just_journals = []
        for i, pub in enumerate(pub_list):
            if 'journal_title' in pub:
                pub['journal_title'] = pub['journal_title'].replace('.', r'.\ ')
                just_journals.append(pub)
        return just_journals

    def format_name(self, person):
        """
        Note:
            Person is transformed into a LaTeX-friendly string like "E.~W.~Dijkstra or J.~von Neumann"

        See Also:
            BaseWriter.format_name
        """
        return super(LatexWriter, self).format_name(person).replace('. ', '.~')

    def format_persons(self, persons):
        """
        See Also:
            BaseWriter.format_persons
        """
        return super(LatexWriter, self).format_persons(persons, "{\it et al.}")

    def write_preamble(self, bib_data):
        """
        See Also:
            BaseWriter.write_preamble
        """
        if len(bib_data.entries) > 1:
            return r"\begin{thebibliography}{" + str(len(bib_data.entries)) + "}\n\n"
        return ""

    def write_postamble(self, bib_data):
        """
        See Also:
            BaseWriter.write_postamble
        """
        if len(bib_data.entries) > 1:
            return "\n\n\\end{thebibliography}"
        else:
            return ""

    def to_string(self, bib_data):
        """
        See Also:
            BaseWriter.to_string
        """
        bib_string = self.write_preamble(bib_data)
        bib_string += '\n\n'.join(self.render_entry(texkey, entry) for texkey, entry in bib_data.entries.items())
        bib_string += self.write_postamble(bib_data)
        return bib_string
