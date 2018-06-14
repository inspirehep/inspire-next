# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2018 CERN.
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

import click
import click_spinner

from flask.cli import with_appcontext

from .checkers import check_unlinked_references


@click.group()
def check():
    """Commands to perform checks on records"""


@check.command()
@click.argument('doi_file_name', type=click.File('w', encoding='utf-8'), default='missing_cited_dois.txt')
@click.argument('arxiv_file_name', type=click.File('w', encoding='utf-8'), default='missing_cited_arxiv_eprints.txt')
@with_appcontext
def unlinked_references(doi_file_name, arxiv_file_name):
    """Find often cited literature that is not on INSPIRE.

    It generates two files with a list of DOI/arxiv ids respectively,
    in which each line has the respective identifier, folowed by two numbers,
    representing the amount of times the literature has been cited
    by a core and a non-core article respectively.
    The lists are ordered by an internal measure of relevance."""
    with click_spinner.spinner():
        click.echo('Looking up unlinked references...')
        result_doi, result_arxiv = check_unlinked_references()

    click.echo('Done!')
    click.echo(u'Output written to "{}" and "{}"'.format(doi_file_name.name, arxiv_file_name.name))

    for item in result_doi:
        doi_file_name.write(u'{i[0]}: {i[1]}\n'.format(i=item))

    for item in result_arxiv:
        arxiv_file_name.write(u'{i[0]}: {i[1]}\n'.format(i=item))
